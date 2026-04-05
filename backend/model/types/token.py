from dataclasses import dataclass
from typing import List

from db.abc.db import DBInterface


@dataclass
class Token:
    id: str
    token_value: str
    description: str
    categories: List[str]

    def write(self, backend: DBInterface) -> str:
        cat_list_hash = backend.insert_id_list(self.categories)
        return backend.insert_obj({
            "id": self.id,
            "token_value": self.token_value,
            "description": self.description,
            "categories": cat_list_hash,
        })

    @staticmethod
    def read(backend: DBInterface, hash: str) -> 'Token':
        raw_token = backend.fetch_obj(hash)
        categories = backend.fetch_id_list(raw_token["categories"])
        return Token(
            id=raw_token["id"],
            token_value=raw_token["token_value"],
            description=raw_token["description"],
            categories=categories,
        )
