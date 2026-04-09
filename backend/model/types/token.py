from dataclasses import dataclass
from typing import List as tList

from marshmallow.fields import String, List
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from util.schema import desc, to_field


@dataclass
class Token:
    id: str = to_field(String(required=True, metadata=desc('ID of the token')))
    token_value: str = to_field(String(required=True, metadata=desc('Value of the token')))
    description: str = to_field(String(required=False, metadata=desc('Description of the token')))
    categories: tList[str] = to_field(List(
        String(required=True, metadata=desc('Category ID')),
        required=True,
        metadata=desc('Categories associated with the token'),
    ))

    def write(self, backend: DBInterface) -> str:
        cat_list_hash = backend.insert_id_list(self.categories)
        return backend.insert_obj({
            "id": self.id,
            "token_value": self.token_value,
            "description": self.description,
            "categories": cat_list_hash,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Token':
        raw_token = backend.fetch_obj(obj_hash)
        categories = backend.fetch_id_list(raw_token["categories"])
        return Token(
            id=raw_token["id"],
            token_value=raw_token["token_value"],
            description=raw_token["description"],
            categories=categories,
        )

token_schema = class_schema(Token)()
