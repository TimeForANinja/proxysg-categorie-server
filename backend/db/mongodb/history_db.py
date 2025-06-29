import uuid
from typing import List, Mapping, Any, Optional
import time
from pymongo.collection import Collection
from pymongo.database import Database

from auth.auth_user import AuthUser
from db.abc.history import HistoryDBInterface, History, Atomic


class MongoDBHistory(HistoryDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection: Collection = db['history']

    def add_history_event(
            self,
            action: str,
            user: AuthUser,
            ref_token: List[str],
            ref_url: List[str],
            ref_category: List[str],
            atomics: Optional[List[Atomic]] = None,
    ) -> History:
        """
        Add a new history event with the given name

        :param action: The action to be recorded
        :param user: The user who performed the action
        :param ref_token: List of token IDs referenced by the action
        :param ref_url: List of URL IDs referenced by the action
        :param ref_category: List of category IDs referenced by the action
        :param atomics: Optional list of atomic changes
        :return: The newly created history event
        """
        timestamp = int(time.time())  # Current UNIX time

        # Convert atomics to dictionaries for MongoDB storage
        atomics_list = []
        if atomics:
            for atomic in atomics:
                atomic.id = str(uuid.uuid4())
                atomics_list.append({
                    'uid': atomic.id,
                    'user': AuthUser.serialize(atomic.user),
                    'action': atomic.action,
                    'description': atomic.description,
                    'time': atomic.timestamp,
                    'ref_token': atomic.ref_token,
                    'ref_url': atomic.ref_url,
                    'ref_category': atomic.ref_category,
                })

        result = self.collection.insert_one({
            'time': timestamp,
            'description': action,
            'atomics': atomics_list,
            'user': AuthUser.serialize(user),
            'ref_token': ref_token,
            'ref_url': ref_url,
            'ref_category': ref_category,
        })

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

    def get_history_events(self) -> List[History]:
        events = self.collection.find({})
        result = []

        for event in events:
            # Convert atomics dictionaries to Atomic objects
            atomics_list = [
                Atomic(
                    id=atomic_dict['uid'],
                    user=AuthUser.unserialize(atomic_dict['user']),
                    action=atomic_dict['action'],
                    description=atomic_dict.get('description'),
                    timestamp=atomic_dict['time'],
                    ref_token=atomic_dict.get('ref_token', []),
                    ref_url=atomic_dict.get('ref_url', []),
                    ref_category=atomic_dict.get('ref_category', []),
                )
                for atomic_dict in event.get('atomics', [])
            ]

            result.append(History(
                id=str(event['_id']),
                time=event['time'],
                description=event.get('description'),
                atomics=atomics_list,
                user=AuthUser.unserialize(event['user']),
                ref_token=event['ref_token'],
                ref_url=event['ref_url'],
                ref_category=event['ref_category'],
            ))

        return result
