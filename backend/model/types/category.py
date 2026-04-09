from dataclasses import dataclass
from typing import List as tList, Optional, Any, Dict

from marshmallow.fields import String, List, Nested
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from model.types.shared import Constraint, constraint_schema
from util.schema import desc, to_field


@dataclass
class Category:
    id: str = to_field(String(required=True, metadata=desc('ID of the Category')))
    name: str = to_field(String(required=True, metadata=desc('Name of the Category')))
    members: tList[Member] = to_field(List(
        String(required=True, metadata=desc('URL Value')),
        required=True,
        metadata=desc(
            'List of URLs that are associated with this Category'
        )
    ))

    def write(self, backend: DBInterface) -> str:
        member_hashes = [
            m.write(backend) for m in self.members
        ]
        member_hashes_list = backend.insert_id_list(member_hashes)
        return backend.insert_obj({
            "id": self.id,
            "name": self.name,
            "members": member_hashes_list,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Category':
        raw_category = backend.fetch_obj(obj_hash)
        member_hash_list = backend.fetch_id_list(raw_category["members"])
        members = [Member.read(backend, member_hash) for member_hash in member_hash_list]
        return Category(
            id=raw_category["id"],
            name=raw_category["name"],
            members=members,
        )


@dataclass
class Member:
    url: str = to_field(String(required=True, metadata=desc('Value of the URL')))
    constraint: Optional[Constraint] = to_field(Nested(
        constraint_schema,
        required=False,
        metadata=desc('Constraint for the URL')
    ))

    def write(self, backend: DBInterface) -> str:
        data: Dict[str, Any] = {
            "url": self.url,
        }
        if self.constraint is not None:
            data["constraint"] = self.constraint.serialize()
        return backend.insert_obj(data)

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Member':
        raw_member = backend.fetch_obj(obj_hash)
        return Member(
            url=raw_member["url"],
            constraint=(
                Constraint.deserialize(raw_member["constraint"])
                if "constraint" in raw_member else None
            ),
        )


category_schema = class_schema(Category)()
member_schema = class_schema(Member)()
