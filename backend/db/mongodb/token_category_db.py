from typing import List, Mapping
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.token_category import TokenCategoryDBInterface


class MongoDBTokenCategory(TokenCategoryDBInterface):
    def __init__(self, db: Database[Mapping[str, any] | any]):
        self.db = db
        self.collection = self.db['tokens']

    def create_table(self) -> None:
        pass

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        row = self.collection.find_one(query)
        if not row:
            return []

        return [
            x['cat']
            for x in row.get("categories", [])
            if x['is_deleted'] == 0
        ]

    def add_token_category(self, token_id: str, category_id: str) -> None:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        update = {"$addToSet": {"categories": {"cat": category_id, "is_deleted": 0}}}

        result = self.collection.update_one(query, update)

        if result.modified_count == 0:
            raise ValueError(f"Token with id {token_id} not found or is deleted.")

    def delete_token_category(self, token_id: str, category_id: str) -> None:
        query = {"_id": ObjectId(token_id), "is_deleted": 0}
        update = {"$set": {"categories.$[elem].is_deleted": 1}}
        array_filters = [{"elem.cat": category_id, "elem.is_deleted": 0}]

        result = self.collection.update_one(query, update, array_filters=array_filters)

        if result.modified_count == 0:
            raise ValueError(f"Token with id {token_id} not found or is deleted.")
