from typing import List, Mapping, Any
import time
from pymongo.collection import Collection
from pymongo.database import Database

from auth.auth_user import AuthUser
from db.history import HistoryDBInterface, History


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
    ) -> History:
        timestamp = int(time.time())  # Current UNIX time
        result = self.collection.insert_one({
            'time': timestamp,
            'description': action,
            'atomics': [],  # Default empty atomics list
            'user': user.username,
            'ref_token': ref_token,
            'ref_url': ref_url,
            'ref_category': ref_category,
        })

        return History(
            id=str(result.inserted_id),
            time=timestamp,
            description=action,
            atomics=[],
            user=user.username,
            ref_token=ref_token,
            ref_url=ref_url,
            ref_category=ref_category,
        )

    def get_history_events(self) -> List[History]:
        events = self.collection.find({})
        result = [
            History(
                id=event['_id'],
                time=event['time'],
                description=event.get('description'),
                atomics=event.get('atomics', []),
                user=event['user'],
                ref_token=event['ref_token'],
                ref_url=event['ref_url'],
                ref_category=event['ref_category'],
            ) for event in events
        ]
        return result
