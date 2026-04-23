import uuid
from dataclasses import dataclass
from typing import List as tList, Callable, Dict
from marshmallow.fields import String, Integer, List
from marshmallow_dataclass import class_schema

from db.abc.constants import TYPE_KEY, TypeIDs
from db.abc.db import DBInterface
from model.types.url import URL
from model.util.list_tld import get_tld_list, get_su_list
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
    def batch_write(backend: DBInterface, categories: tList['Category']) -> tList[str]:
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
    def batch_read(backend: DBInterface, obj_hashes: tList[str]) -> tList['Category']:
        raw_categories = backend.batch_fetch_obj(obj_hashes)
        return [
            Category(
                id=c["id"],
                name=c["name"],
                description=c["description"],
                color=c["color"],
            ) for c in raw_categories
        ] + PREDEFINED_CATEGORIES


category_schema = class_schema(Category)()


@dataclass
class ExternalCategory(Category):
    items: tList[str] = to_field(List(String(), required=True, metadata=desc("List of items in the category")))

    def __init__(self, obj_id: str, name: str, get_description: Callable[[], str], get_items: Callable[[], tList[str]]):
        super().__init__(
            id=obj_id,
            name=name,
            description=get_description(),
            color=0,
        )
        self.items = get_items()

    def get_items(self) -> Dict[str, URL]:
        return {
            u.id: u
            for u in [
                URL.new(x, f"Generated for External Category {self.name}")
                for x in self.items
            ]
        }


PREDEFINED_CATEGORIES: tList[ExternalCategory] = [
    ExternalCategory(
        "LIST_RFC_SPECIAL_USE",
        "RFC-Listed-Special-Use-URLs",
        lambda: get_su_list()[1],
        lambda: get_su_list()[0],
    ),

    ExternalCategory(
        "LIST_TLD",
        "Public-TLDs",
        lambda: get_tld_list()[1],
        lambda: get_tld_list()[0],
    )
]
