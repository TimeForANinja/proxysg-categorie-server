from typing import List, Mapping, Any
from pymongo.synchronous.database import Database

from db.abc.staging import StagedChange, MutableStagedChange, StagingDBInterface


class MongoDBStaging(StagingDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection = self.db['categories']

    # TODO: implement
    def store_staged_change(self, change: MutableStagedChange) -> None:
        pass

    def get_staged_changes(self) -> List[StagedChange]:
        pass

    def clear_staged_changes(self) -> None:
        pass
