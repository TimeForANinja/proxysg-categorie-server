import uuid
from dataclasses import dataclass
from marshmallow.fields import String
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from util.schema import desc, to_field


@dataclass
class Category:
    id: str = to_field(String(required=True, metadata=desc('ID of the Category')))
    name: str = to_field(String(required=True, metadata=desc('Name of the Category')))

    @staticmethod
    def new(name: str) -> 'Category':
        return Category(
            id=str(uuid.uuid4()),
            name=name
        )

    def write(self, backend: DBInterface) -> str:
        return backend.insert_obj({
            "id": self.id,
            "name": self.name,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Category':
        raw_category = backend.fetch_obj(obj_hash)
        return Category(
            id=raw_category["id"],
            name=raw_category["name"],
        )


category_schema = class_schema(Category)()
