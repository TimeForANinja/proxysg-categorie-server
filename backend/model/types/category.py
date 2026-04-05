from dataclasses import dataclass
from typing import List

from db.abc.db import DBInterface


@dataclass
class Category:
    id: str
    name: str
    members: List[str]

    def write(self, backend: DBInterface) -> str:
        member_list_hash = backend.insert_id_list(self.members)
        return backend.insert_obj({
            "id": self.id,
            "name": self.name,
            "members": member_list_hash,
        })

    @staticmethod
    def read(backend: DBInterface, hash: str) -> 'Category':
        raw_category = backend.fetch_obj(hash)
        members = backend.fetch_id_list(raw_category["members"])
        return Category(
            id=raw_category["id"],
            name=raw_category["name"],
            members=members,
        )


@dataclass
class Member:
    url: str
    constraint: Constraint

    def write(self, backend: DBInterface) -> str:
        return backend.insert_obj({
            "url": self.url,
            "constraint": self.constraint,
        })

    @staticmethod
    def read(backend: DBInterface, hash: str) -> 'Member':
        raw_member = backend.fetch_obj(hash)
        return Member(
            url=raw_member["url"],
            constraint=raw_member["constraint"],
        )


@dataclass
class Constraint:
    from_: int
    until: int
    comment: str
