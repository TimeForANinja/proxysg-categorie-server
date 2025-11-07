from typing import List, Mapping, Any, Dict, Optional
from pymongo.synchronous.database import Database

from auth.auth_user import AuthUser
from db.backend.abc.util.types import MyTransactionType
from db.backend.abc.staging import StagingDBInterface
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs
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

    def store_staged_change(self, change: StagedChange):
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

    def store_staged_changes(self, changes: List[StagedChange]):
        """Store a list of staged changes in the MongoDB database (batch)."""
        if not changes:
            return

        documents = [
            {
                'action_type': ch.action_type.value,
                'action_table': ch.action_table.value,
                'auth': AuthUser.serialize(ch.auth),
                'uid': ch.uid,
                'data': ch.data,
                'timestamp': ch.timestamp,
            }
            for ch in changes
        ]
        # Use insert_many for efficient batch insert
        self.collection.insert_many(documents, ordered=False)

    def get_staged_changes(self, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        """Get all staged changes from the MongoDB database."""
        documents = self.collection.find(**mongo_transaction_kwargs(session))
        return [_document_to_staged_change(doc) for doc in documents]

    def get_staged_changes_by_table(self, table: ActionTable, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        """Get all staged changes for a specific table from the MongoDB database."""
        documents = self.collection.find({'action_table': table.value}, **mongo_transaction_kwargs(session))
        return [_document_to_staged_change(doc) for doc in documents]

    def get_staged_changes_by_table_and_id(
        self,
        table: ActionTable,
        obj_id: str,
        session: Optional[MyTransactionType] = None,
    ) -> List[StagedChange]:
        documents = self.collection.find({'action_table': table.value, 'uid': obj_id}, **mongo_transaction_kwargs(session))
        return [_document_to_staged_change(doc) for doc in documents]

    def clear_staged_changes(self, before: int = None, session: Optional[MyTransactionType] = None):
        """Clear all staged changes from the MongoDB database."""
        if before is not None:
            self.collection.delete_many({'timestamp': {'$lte': before}}, **mongo_transaction_kwargs(session))
        else:
            self.collection.delete_many({}, **mongo_transaction_kwargs(session))
