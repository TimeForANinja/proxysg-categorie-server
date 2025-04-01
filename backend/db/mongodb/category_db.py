from typing import Optional, List, Mapping
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from db.category import CategoryDBInterface, MutableCategory, Category


def _build_category(row: Mapping[str, any]) -> Category:
    return Category(
        id=row["_id"],
        name=row["name"],
        color=row["color"],
        description=row.get("description"),
        is_deleted=row["is_deleted"],
        nested_categories=[x['cat'] for x in row.get("nested_categories", [])]
    )


class MongoDBCategory(CategoryDBInterface):
    def __init__(self, db: Database[Mapping[str, any] | any]):
        self.db = db
        self.collection = self.db['categories']

    def create_table(self) -> None:
        pass

    def add_category(self, category: MutableCategory) -> Category:
        result = self.collection.insert_one({
            "name": category.name,
            "color": category.color,
            "description": category.description,
            "is_deleted": 0,
            "nested_categories": []
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
        query = {"_id": ObjectId(category_id), "is_deleted": 0}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_category(row)

    def update_category(self, cat_id: str, category: MutableCategory) -> Category:
        query = {"_id": ObjectId(cat_id), "is_deleted": 0}
        update_fields = {
            "name": category.name,
            "color": category.color,
            "description": category.description
        }

        result = self.collection.update_one(query, {"$set": update_fields})

        if result.matched_count == 0:
            raise ValueError(f"Category with ID {cat_id} not found or is deleted.")

        # Return the updated category
        return self.get_category(cat_id)

    def delete_category(self, category_id: str) -> None:
        query = {"_id": ObjectId(category_id), "is_deleted": 0}
        update = {"$set": {"is_deleted": 1}}
        result = self.collection.update_one(query, update)

        if result.matched_count == 0:
            raise ValueError(f"Category with ID {category_id} not found or already deleted.")

    def get_all_categories(self) -> List[Category]:
        rows = self.collection.find({"is_deleted": 0})
        return [
            _build_category(row)
            for row in rows
        ]
