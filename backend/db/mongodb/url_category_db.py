from typing import List, Mapping
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.url_category import UrlCategoryDBInterface


class MongoDBURLCategory(UrlCategoryDBInterface):
    def __init__(self, db: Database[Mapping[str, any] | any]):
        self.db = db
        self.collection = self.db['urls']

    def create_table(self) -> None:
        pass

    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        query = {"_id": ObjectId(url_id), "is_deleted": 0}
        row = self.collection.find_one(query)
        if not row:
            return []

        return [
            x['cat']
            for x in row.get("categories", [])
            if x['is_deleted'] == 0
        ]

    def add_url_category(self, url_id: str, category_id: str) -> None:
        query = {"_id": ObjectId(url_id), "is_deleted": 0}
        update = {"$addToSet": {"categories": {"cat": category_id, "is_deleted": 0}}}

        result = self.collection.update_one(query, update)

        if result.modified_count == 0:
            raise ValueError(f"URL with id {url_id} not found or is deleted.")

    def delete_url_category(self, url_id: str, category_id: str) -> None:
        query = {"_id": ObjectId(url_id), "is_deleted": 0}
        update = {"$set": {"categories.$[elem].is_deleted": 1}}
        array_filters = [{"elem.cat": category_id, "elem.is_deleted": 0}]

        result = self.collection.update_one(query, update, array_filters=array_filters)

        if result.modified_count == 0:
            raise ValueError(f"URL with id {url_id} not found or is deleted.")
