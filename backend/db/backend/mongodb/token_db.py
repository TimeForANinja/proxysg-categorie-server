import time
from typing import Optional, List, Mapping, Any
from pymongo.synchronous.database import Database

from db.backend.abc.token import TokenDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs
from db.dbmodel.token import MutableToken, Token


def _build_token(row: Mapping[str, Any]) -> Token:
    """build a Token object from a MongoDB document"""
    return Token(
        id=str(row['uid']),
        token=row['token'],
        description=row.get('description'),
        last_use=row['last_use'],
        is_deleted=row['is_deleted'],
        categories=[
            x['cat']
            for x in row.get('categories', [])
            if x['is_deleted'] == 0
        ],
        pending_changes=False,
    )


class MongoDBToken(TokenDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection = self.db['tokens']

    def add_token(self, token_id: str, uuid: str, mut_tok: MutableToken, session: Optional[MyTransactionType] = None) -> Token:
        self.collection.insert_one({
            'uid': token_id,
            'token': uuid,
            'description': mut_tok.description,
            'last_use': 0,
            'is_deleted': 0,
            'categories': []
        }, **mongo_transaction_kwargs(session))

        return Token.from_mutable(token_id, uuid, mut_tok)

    def get_token(self, token_id: str, session: Optional[MyTransactionType] = None) -> Optional[Token]:
        query = {'uid': token_id, 'is_deleted': 0}
        row = self.collection.find_one(query, **mongo_transaction_kwargs(session))
        if not row:
            return None

        return _build_token(row)

    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        query = {'token': token_uuid, 'is_deleted': 0}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_token(row)

    def update_token(self, token_id: str, token: MutableToken, session: Optional[MyTransactionType] = None) -> Token:
        query = {'uid': token_id, 'is_deleted': 0}
        update_fields = {
            'description': token.description,
        }

        result = self.collection.update_one(query, {'$set': update_fields}, **mongo_transaction_kwargs(session))

        if result.matched_count == 0:
            raise ValueError(f'Token with ID {token_id} not found or is deleted.')

        return self.get_token(token_id)

    def update_usage(self, token_id: str):
        query = {'uid': token_id, 'is_deleted': 0}
        update_fields = {
            'last_use': int(time.time()),
        }

        result = self.collection.update_one(query, {'$set': update_fields})

        if result.matched_count == 0:
            raise ValueError(f'Token with ID {token_id} not found or is deleted.')

    def roll_token(self, token_id: str, uuid: str, session: Optional[MyTransactionType] = None) -> Token:
        query = {'uid': token_id, 'is_deleted': 0}
        update_fields = {
            'token': uuid,
        }

        result = self.collection.update_one(query, {'$set': update_fields}, **mongo_transaction_kwargs(session))

        if result.matched_count == 0:
            raise ValueError(f'Token with ID {token_id} not found or is deleted.')

        return self.get_token(token_id)

    def delete_token(self, token_id: str, del_timestamp: int, session: Optional[MyTransactionType] = None):
        query = {'uid': token_id, 'is_deleted': 0}
        update = {'$set': {'is_deleted': del_timestamp}}
        result = self.collection.update_one(query, update, **mongo_transaction_kwargs(session))

        if result.matched_count == 0:
            raise ValueError(f'Token with ID {token_id} not found or already deleted.')

    def get_all_tokens(self, session: Optional[MyTransactionType] = None) -> List[Token]:
        rows = self.collection.find({ 'is_deleted': 0 }, **mongo_transaction_kwargs(session))
        return [
            _build_token(row)
            for row in rows
        ]
