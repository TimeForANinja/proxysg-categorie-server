from typing import List, Mapping, Any, TypeVar, Generic
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

T = TypeVar('T')

class MongoDBBaseCategory(Generic[T]):
    """
    Base class for MongoDB category implementations to reduce code duplication.

    It allows to interact with simple XYZ <-> Category mappings.
    """
    def __init__(self, db: Database[Mapping[str, Any] | Any], collection_name: str, item_type: str):
        self.db = db
        self.collection = self.db[collection_name]
        self.item_type = item_type

    def get_categories_by_item(self, item_id: str) -> List[str]:
        """
        Get all categories of an item
        
        :param item_id: The ID of the item
        """
        query = {'_id': ObjectId(item_id), 'is_deleted': 0}
        row = self.collection.find_one(query)
        if not row:
            return []

        return [
            x['cat']
            for x in row.get('categories', [])
            if x['is_deleted'] == 0
        ]

    def add_item_category(self, item_id: str, category_id: str) -> None:
        """
        Add a new mapping of item and Category
        
        :param item_id: The ID of the item
        :param category_id: The ID of the Category
        """
        query = {'_id': ObjectId(item_id), 'is_deleted': 0}
        update = {'$addToSet': {'categories': {'cat': category_id, 'is_deleted': 0}}}

        result = self.collection.update_one(query, update)

        if result.modified_count == 0:
            raise ValueError(f'{self.item_type} with id {item_id} not found or is deleted.')

    def delete_item_category(self, item_id: str, category_id: str) -> None:
        """
        Delete a mapping of item and Category.
        
        :param item_id: The ID of the item
        :param category_id: The ID of the Category
        """
        query = {'_id': ObjectId(item_id), 'is_deleted': 0}
        update = {'$set': {'categories.$[elem].is_deleted': 1}}
        array_filters = [{'elem.cat': category_id, 'elem.is_deleted': 0}]

        result = self.collection.update_one(query, update, array_filters=array_filters)

        if result.modified_count == 0:
            raise ValueError(f'{self.item_type} with id {item_id} not found or is deleted.')