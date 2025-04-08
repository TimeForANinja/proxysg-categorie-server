import time
from typing import Optional, List, Mapping
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.token import TokenDBInterface, MutableToken, Token


def _build_token(row: Mapping[str, any]) -> Token:
    """build a Token object from a MongoDB document"""
    return Token(
        id=str(row["_id"]),
        token=row["token"],
        description=row.get("description"),
        last_use=row["last_use"],
        is_deleted=row["is_deleted"],
        categories=[
            x['cat']
            for x in row.get("categories", [])
            if x['is_deleted'] == 0
        ],
    )


class MongoDBToken(TokenDBInterface):
    def __init__(self, db: Database[Mapping[str, any] | any]):
        self.db = db
        self.collection = self.db['tokens']

    def create_table(self) -> None:
        self.collection.create_index({"token": 1}, unique=True)

    def add_token(self, uuid: str, mut_tok: MutableToken) -> Token:
        result = self.collection.insert_one({
            "token": uuid,
            "description": mut_tok.description,
            "last_use": 0,
            "is_deleted": 0,
            "categories": []
        })

        return Token(
            id=str(result.inserted_id),
            token=uuid,
            description=mut_tok.description,
            last_use=0,
            is_deleted=0,
            categories=[]
        )

    def get_token(self, token_id: str) -> Optional[Token]:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_token(row)

    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        query = {"token": token_uuid, "is_deleted": 0}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_token(row)

    def update_token(self, token_id: str, token: MutableToken) -> Token:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        update_fields = {
            "description": token.description,
        }

        result = self.collection.update_one(query, {"$set": update_fields})

        if result.matched_count == 0:
            raise ValueError(f"Token with ID {token_id} not found or is deleted.")

        return self.get_token(token_id)

    def update_usage(self, token_id: str) -> None:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        update_fields = {
            "last_use": int(time.time()),
        }

        result = self.collection.update_one(query, {"$set": update_fields})

        if result.matched_count == 0:
            raise ValueError(f"Token with ID {token_id} not found or is deleted.")

    def roll_token(self, token_id: str, uuid: str) -> Token:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        update_fields = {
            "token": uuid,
        }

        result = self.collection.update_one(query, {"$set": update_fields})

        if result.matched_count == 0:
            raise ValueError(f"Token with ID {token_id} not found or is deleted.")

        return self.get_token(token_id)

    def delete_token(self, token_id: str) -> None:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        update = {"$set": {"is_deleted": 1}}
        result = self.collection.update_one(query, update)

        if result.matched_count == 0:
            raise ValueError(f"Token with ID {token_id} not found or already deleted.")

    def get_all_tokens(self) -> List[Token]:
        rows = self.collection.find({ "is_deleted": 0 })
        return [
            _build_token(row)
            for row in rows
        ]
