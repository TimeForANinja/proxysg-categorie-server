import time
from typing import Optional, List, Mapping, Any
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.category import CategoryDBInterface, MutableCategory, Category


def _build_category(row: Mapping[str, Any]) -> Category:
    """build a Category object from a MongoDB document"""
    return Category(
        id=str(row['_id']),
        name=row['name'],
        color=row['color'],
        description=row.get('description'),
        is_deleted=row['is_deleted'],
        nested_categories=[
            x['cat']
            for x in row.get('nested_categories', [])
            if x['is_deleted'] == 0
        ]
    )


class MongoDBCategory(CategoryDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection = self.db['categories']

    def add_category(self, category: MutableCategory) -> Category:
        result = self.collection.insert_one({
            'name': category.name,
            'color': category.color,
            'description': category.description,
            'is_deleted': 0,
            'nested_categories': []
        })

        return Category(
            id=str(result.inserted_id),
            name=category.name,
            color=category.color,
            description=category.description,
            is_deleted=0,
            nested_categories=[]
        )

    def get_category(self, category_id: str) -> Optional[Category]:
        query = {'_id': ObjectId(category_id), 'is_deleted': 0}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_category(row)

    def update_category(self, cat_id: str, category: MutableCategory) -> Category:
        query = {'_id': ObjectId(cat_id), 'is_deleted': 0}
        update_fields = {
            'name': category.name,
            'color': category.color,
            'description': category.description
        }

        result = self.collection.update_one(query, {'$set': update_fields})

        if result.matched_count == 0:
            raise ValueError(f'Category with ID {cat_id} not found or is deleted.')

        # Return the updated category
        return self.get_category(cat_id)

    def delete_category(self, category_id: str) -> None:
        current_timestamp = int(time.time())

        query = {'_id': ObjectId(category_id), 'is_deleted': 0}
        update = {'$set': {'is_deleted': current_timestamp}}
        result = self.collection.update_one(query, update)

        if result.matched_count == 0:
            raise ValueError(f'Category with ID {category_id} not found or already deleted.')

        # delete it from all other collections
        update2 = {'$set': {'nested_categories.$[elem].is_deleted': current_timestamp}}
        update3 = {'$set': {'categories.$[elem].is_deleted': current_timestamp}}
        array_filters2 = [{'elem.cat': category_id, 'elem.is_deleted': 0}]

        self.db['categories'].update_many({}, update2, array_filters=array_filters2)
        self.db['urls'].update_many({}, update3, array_filters=array_filters2)
        self.db['tokens'].update_many({}, update3, array_filters=array_filters2)

    def get_all_categories(self) -> List[Category]:
        rows = self.collection.find({ 'is_deleted': 0 })
        return [
            _build_category(row)
            for row in rows
        ]
