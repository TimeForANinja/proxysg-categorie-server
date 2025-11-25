from typing import List, Mapping, Any, Optional
import time
from pymongo.collection import Collection
from pymongo.database import Database

from auth.auth_user import AuthUser
from db.backend.abc.util.types import MyTransactionType
from db.backend.abc.history import HistoryDBInterface
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs
from db.dbmodel.history import History, Atomic


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

        # store the history id, so we can use it when inserting atomics
        history_id = result.inserted_id

        # prepare atomics for insertion
        atomics_list = atomics or []
        if atomics_list:
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
                for a in atomics_list
            ]
            # insert_many respects session via kwargs
            self.atomics_collection.insert_many(docs, **mongo_transaction_kwargs(session))

        # return the History object including embedded atomics
        return History(
            id=str(history_id),
            time=timestamp,
            description=action,
            atomics=atomics_list,
            user=user,
            ref_token=ref_token,
            ref_url=ref_url,
            ref_category=ref_category,
        )

    def has_history_events(self) -> bool:
        # required for migration, since the get_history_events can fail pre-migration
        return self.collection.count_documents({}) > 0

    def get_history_events(self) -> List[History]:
        # Fetch all history events first
        event_docs = list(self.collection.find({}))
        result: List[History] = []

        if not event_docs:
            # shortcut to improve performance
            return result

        # fetch all atomics, since we also fetched all history events
        atomics_docs = list(self.atomics_collection.find({}))

        # Group atomics by history_id
        atomics_by_history: dict[Any, List[Atomic]] = {}
        for doc in atomics_docs:
            atomic_obj = Atomic(
                id=doc['uid'],
                user=AuthUser.unserialize(doc['user']),
                action=doc['action'],
                description=doc['description'],
                time=doc['time'],
                ref_token=doc.get('ref_token', []),
                ref_url=doc.get('ref_url', []),
                ref_category=doc.get('ref_category', []),
            )
            atomics_by_history.setdefault(doc['history_id'], []).append(atomic_obj)

        # Build History objects with their associated atomics
        for event in event_docs:
            history_id = event['_id']
            atomics_list = atomics_by_history.get(history_id, [])
            result.append(History(
                id=str(history_id),
                time=event['time'],
                description=event['description'],
                atomics=atomics_list,
                user=AuthUser.unserialize(event['user']),
                ref_token=event.get('ref_token', []),
                ref_url=event.get('ref_url', []),
                ref_category=event.get('ref_category', []),
            ))

        return result
