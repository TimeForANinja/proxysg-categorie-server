from typing import List, Mapping, Any, Dict
from pymongo.synchronous.database import Database

from auth.auth_user import AuthUser
from db.backend.abc.staging import StagingDBInterface
from db.dbmodel.staging import StagedChange, ActionType, ActionTable


def _document_to_staged_change(doc: Dict[str, Any]) -> StagedChange:
    """Convert a MongoDB document to a StagedChange object."""
    return StagedChange(
        action_type=ActionType(doc['action_type']),
        action_table=ActionTable(doc['action_table']),
        auth=AuthUser.unserialize(doc['auth']),
        uid=doc['uid'],
        data=doc.get('data'),
        timestamp=doc['timestamp'],
    )


class MongoDBStaging(StagingDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection = self.db['staged_changes']

    def store_staged_change(self, change: StagedChange) -> None:
        """Store a staged change in the MongoDB database."""
        document = {
            'action_type': change.action_type.value,
            'action_table': change.action_table.value,
            'auth': AuthUser.serialize(change.auth),
            'uid': change.uid,
            'data': change.data,
            'timestamp': change.timestamp
        }
        self.collection.insert_one(document)

    def get_staged_changes(self) -> List[StagedChange]:
        """Get all staged changes from the MongoDB database."""
        documents = self.collection.find()
        return [_document_to_staged_change(doc) for doc in documents]

    def clear_staged_changes(self) -> None:
        """Clear all staged changes from the MongoDB database."""
        self.collection.delete_many({})
