from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from db.abc.constants import TYPE_KEY, TypeIDs
from db.abc.db import DBInterface
from model.types.shared import Constraint


@dataclass
class TokenCategoryMapping:
    token_id: str
    category_id: str

    @staticmethod
    def batch_write(backend: DBInterface, mappings: List['TokenCategoryMapping']) -> List[str]:
        return backend.batch_insert_obj([
            {
                TYPE_KEY: TypeIDs.TYPE_ID_TOKEN_CAT_MAP,
                "token_id": m.token_id,
                "category_id": m.category_id,
            } for m in mappings
        ])

    @staticmethod
    def batch_read(backend: DBInterface, obj_hashes: List[str]) -> List['TokenCategoryMapping']:
        raw_mappings = backend.batch_fetch_obj(obj_hashes)
        return [
            TokenCategoryMapping(
                token_id=m["token_id"],
                category_id=m["category_id"],
            ) for m in raw_mappings
        ]


@dataclass
class URLCategoryMapping:
    url_id: str
    category_id: str
    constraint: Optional[Constraint]

    @staticmethod
    def batch_write(backend: DBInterface, mappings: List['URLCategoryMapping']) -> List[str]:
        return backend.batch_insert_obj([
            {
                TYPE_KEY: TypeIDs.TYPE_ID_URL_CAT_MAP,
                "url_id": m.url_id,
                "category_id": m.category_id,
                "constraint": m.constraint.serialize() if m.constraint is not None else None,
            } for m in mappings
        ])

    @staticmethod
    def batch_read(backend: DBInterface, obj_hashes: List[str]) -> List['URLCategoryMapping']:
        raw_mappings = backend.batch_fetch_obj(obj_hashes)
        return [
            URLCategoryMapping(
                url_id=m["url_id"],
                category_id=m["category_id"],
                constraint=(
                    Constraint.deserialize(m["constraint"]) if m["constraint"] is not None else None
                ),
            ) for m in raw_mappings
        ]

    def deactivated_by_constraint(self) -> bool:
        """Check if the URL is deactivated by the constraint."""
        now_ts = int(datetime.now().timestamp())
        if not self.constraint:
            return False

        if self.constraint.start != -1 and self.constraint.start > now_ts:
            return True
        if self.constraint.end != -1 and self.constraint.end < now_ts:
            return True
        return False


@dataclass
class ChildCategoryMapping:
    category_id: str
    child_category_id: str

    @staticmethod
    def batch_write(backend: DBInterface, mappings: List['ChildCategoryMapping']) -> List[str]:
        return backend.batch_insert_obj([
            {
                TYPE_KEY: TypeIDs.TYPE_ID_URL_CAT_MAP,
                "category_id": m.category_id,
                "child_category_id": m.child_category_id,
            } for m in mappings
        ])

    @staticmethod
    def batch_read(backend: DBInterface, obj_hashes: List[str]) -> List['ChildCategoryMapping']:
        raw_mappings = backend.batch_fetch_obj(obj_hashes)
        return [
            ChildCategoryMapping(
                category_id=m["category_id"],
                child_category_id=m["child_category_id"],
            ) for m in raw_mappings
        ]
