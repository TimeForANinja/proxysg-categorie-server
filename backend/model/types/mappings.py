from dataclasses import dataclass
from typing import Optional, Any, Dict

from db.abc.db import DBInterface
from model.types.shared import Constraint


@dataclass
class TokenCategoryMapping:
    token_id: str
    category_id: str

    def write(self, backend: DBInterface) -> str:
        return backend.insert_obj({
            "token_id": self.token_id,
            "category_id": self.category_id,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'TokenCategoryMapping':
        raw_mapping = backend.fetch_obj(obj_hash)
        return TokenCategoryMapping(
            token_id=raw_mapping["token_id"],
            category_id=raw_mapping["category_id"],
        )


@dataclass
class URLCategoryMapping:
    url_id: str
    category_id: str
    constraint: Optional[Constraint]

    def write(self, backend: DBInterface) -> str:
        data: Dict[str, Any] = {
            "url_id": self.url_id,
            "category_id": self.category_id,
        }
        if self.constraint is not None:
            data["constraint"] = self.constraint.serialize()
        return backend.insert_obj(data)

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'URLCategoryMapping':
        raw_mapping = backend.fetch_obj(obj_hash)
        return URLCategoryMapping(
            url_id=raw_mapping["url_id"],
            category_id=raw_mapping["category_id"],
            constraint=(
                Constraint.deserialize(raw_mapping["constraint"])
                if "constraint" in raw_mapping else None
            ),
        )
