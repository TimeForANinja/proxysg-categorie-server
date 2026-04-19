import uuid
from dataclasses import dataclass
from typing import List
from marshmallow.fields import String, Integer
from marshmallow_dataclass import class_schema

from db.abc.constants import TYPE_KEY, TypeIDs
from db.abc.db import DBInterface
from util.schema import desc, to_field


@dataclass
class Category:
    id: str = to_field(String(required=True, metadata=desc("ID of the Category")))
    name: str = to_field(String(required=True, metadata=desc("Name of the Category")))
    description: str = to_field(String(required=True, metadata=desc("Description of the Category")))
    color: int = to_field(Integer(required=True, metadata=desc("Color of the Category")))

    @staticmethod
    def new(name: str, description: str) -> 'Category':
        return Category(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            color=0,
        )

    @staticmethod
    def batch_write(backend: DBInterface, categories: List['Category']) -> List[str]:
        return backend.batch_insert_obj([
            {
                TYPE_KEY: TypeIDs.TYPE_ID_CATEGORY,
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "color": c.color,
            } for c in categories
        ])

    @staticmethod
    def batch_read(backend: DBInterface, obj_hashes: List[str]) -> List['Category']:
        raw_categories = backend.batch_fetch_obj(obj_hashes)
        return [
            Category(
                id=c["id"],
                name=c["name"],
                description=c["description"],
                color=c["color"],
            ) for c in raw_categories
        ]


category_schema = class_schema(Category)()
