from typing import List, Mapping, Any, Optional
import time
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from auth.auth_user import AuthUser
from db.backend.abc.util.types import MyTransactionType
from db.backend.abc.history import HistoryDBInterface
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs
from db.dbmodel.history import History, Atomic
from log import log_debug


def _build_atomic(row: Mapping[str, Any]) -> Atomic:
    """build an Atomic object from a MongoDB document"""
    return Atomic(
        id=row['uid'],
        user=AuthUser.unserialize(row['user']),
        action=row['action'],
        description=row['description'],
        time=row['time'],
        ref_token=row.get('ref_token', []),
        ref_url=row.get('ref_url', []),
        ref_category=row.get('ref_category', []),
    )


class MongoDBHistory(HistoryDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection: Collection = db['history']
        self.atomics_collection: Collection = db['history_atomics']

    def add_history_event(
        self,
        action: str,
        user: AuthUser,
        ref_token: List[str],
        ref_url: List[str],
        ref_category: List[str],
        atomics: Optional[List[Atomic]] = None,
        session: Optional[MyTransactionType] = None,
    ) -> History:
        """
        Add a new history event with the given name

        :param action: The action to be recorded
        :param user: The user who performed the action
        :param ref_token: List of token IDs referenced by the action
        :param ref_url: List of URL IDs referenced by the action
        :param ref_category: List of category IDs referenced by the action
        :param atomics: Optional list of atomic changes
        :param session: Optional database session to use
        :return: The newly created history event
        """
        # prepare timestamp (current UNIX time)
        timestamp = int(time.time())

        # first, insert the history event WITHOUT embedding atomics to avoid large docs
        result = self.collection.insert_one({
            'time': timestamp,
            'description': action,
            'user': AuthUser.serialize(user),
            'ref_token': ref_token,
            'ref_url': ref_url,
            'ref_category': ref_category,
        }, **mongo_transaction_kwargs(session))

        self._add_atomics(result.inserted_id, atomics, session=session)

        # return the History object including embedded atomics
        return History(
            id=str(result.inserted_id),
            time=timestamp,
            description=action,
            atomics=atomics or [],
            user=user,
            ref_token=ref_token,
            ref_url=ref_url,
            ref_category=ref_category,
        )

    def _add_atomics(
        self,
        history_id: Any,
        atomics: Optional[List[Atomic]],
        session: Optional[MyTransactionType] = None,
    ):
        """Utility method to insert atomics for a given history event."""
        if not atomics:
            return
        # prepare atomics for insertion
        docs = [
            {
                'history_id': history_id,
                'uid': a.id,
                'user': AuthUser.serialize(a.user),
                'action': a.action,
                'description': a.description,
                'time': a.time,
                'ref_token': a.ref_token,
                'ref_url': a.ref_url,
                'ref_category': a.ref_category,
            }
            for a in atomics
        ]

        # insert_many respects session via kwargs
        self.atomics_collection.insert_many(docs, **mongo_transaction_kwargs(session))


    def get_history_events(self, include_atomics: bool = False) -> List[History]:
        # Fetch all history events first
        event_docs = list(self.collection.find({}))
        result: List[History] = []

        if not event_docs:
            # shortcut to improve performance
            return result

        # fetch all atomics
        # no filter, since we also didn't filter the history events
        # if include_atomics is false, this will simply be an empty list but not break future code
        atomics_docs = []
        if include_atomics:
            atomics_docs = list(self.atomics_collection.find({}))

        # parse atomics and group them by history_id
        atomics_by_history: dict[Any, List[Atomic]] = {}
        for doc in atomics_docs:
            atomics_by_history.setdefault(doc['history_id'], []).append(_build_atomic(doc))

        # Build History objects with their associated atomics
        for event in event_docs:
            history_id = event['_id']
            result.append(History(
                id=str(history_id),
                time=event['time'],
                description=event['description'],
                atomics=atomics_by_history.get(history_id, []),
                user=AuthUser.unserialize(event['user']),
                ref_token=event.get('ref_token', []),
                ref_url=event.get('ref_url', []),
                ref_category=event.get('ref_category', []),
            ))

        return result

    def get_history_atomics(
        self,
        references_history: Optional[List[str]] = None,
        references_url: Optional[List[str]] = None,
        references_token: Optional[List[str]] = None,
        references_category: Optional[List[str]] = None,
    ) -> List[Atomic]:
        # Build the OR conditions only for non-empty references
        or_conditions = []
        if references_history:
            or_conditions.append({'history_id': {'$in': [ObjectId(x) for x in references_history]}})
        if references_url:
            # MongoDB will match if the arrays share any elements
            or_conditions.append({'ref_url': {'$in': references_url}})
        if references_token:
            or_conditions.append({'ref_token': {'$in': references_token}})
        if references_category:
            or_conditions.append({'ref_category': {'$in': references_category}})

        log_debug('MONGODB', 'MongoDBHistory#get_history_atomics', {
            'or_conditions': or_conditions,
        })

        # If no conditions match, we return an empty list
        if not or_conditions:
            return []

        # Execute in a single query with $or operator
        atomic_docs = self.atomics_collection.find({'$or': or_conditions})

        # Convert documents to Atomic objects
        return [
            _build_atomic(doc)
            for doc in atomic_docs
        ]
