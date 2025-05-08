from typing import List, Mapping, Any
import time
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.abc.sub_category import SubCategoryDBInterface


class MongoDBSubCategory(SubCategoryDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection = self.db['categories']

    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        query = {'_id': ObjectId(category_id), 'is_deleted': 0}
        row = self.collection.find_one(query)
        if not row:
            return []

        return [
            x['cat']
            for x in row.get('nested_categories', [])
            if x['is_deleted'] == 0
        ]

    def add_sub_category(self, category_id: str, sub_category_id: str) -> None:
        query = {'_id': ObjectId(category_id), 'is_deleted': 0}
        update = {'$addToSet': {'nested_categories': {'cat': sub_category_id, 'is_deleted': 0}}}

        result = self.collection.update_one(query, update)

        if result.modified_count == 0:
            raise ValueError(f'Category with id {category_id} not found or is deleted.')

    def delete_sub_category(self, category_id: str, sub_category_id: str) -> None:
        query = {'_id': ObjectId(category_id), 'is_deleted': 0}
        update = {'$set': {'nested_categories.$[elem].is_deleted': int(time.time())}}
        array_filters = [{'elem.cat': sub_category_id, 'elem.is_deleted': 0}]

        result = self.collection.update_one(query, update, array_filters=array_filters)

        if result.modified_count == 0:
            raise ValueError(f'Category with id {category_id} not found or is deleted.')
