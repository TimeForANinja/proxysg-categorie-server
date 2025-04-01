from typing import List
import time
from pymongo.collection import Collection
from pymongo.database import Database

from db.history import HistoryDBInterface, History


class MongoDBHistory(HistoryDBInterface):
    def __init__(self, db: Database):
        self.db = db
        self.collection: Collection = db['history']

    def create_table(self) -> None:
        pass

    def add_history_event(self, action: str) -> History:
        timestamp = int(time.time())  # Current UNIX time
        result = self.collection.insert_one({
            "time": timestamp,
            "description": action,
            "atomics": []  # Default empty atomics list
        })

        return History(
            id=str(result.inserted_id),
            time=timestamp,
            description=action,
            atomics=[]
        )

    def get_history_events(self) -> List[History]:
        events = self.collection.find({})
        result = [
            History(
                id=event["_id"],
                time=event["time"],
                description=event.get("description"),
                atomics=event.get("atomics", []),
            ) for event in events
        ]
        return result
