import uuid
from dataclasses import dataclass
from typing import List
from marshmallow.fields import String
from marshmallow_dataclass import class_schema

from db.abc.constants import TYPE_KEY, TypeIDs
from db.abc.db import DBInterface
from util.schema import desc, to_field


@dataclass
class Token:
    id: str = to_field(String(required=True, metadata=desc("ID of the token")))
    token_value: str = to_field(String(required=True, metadata=desc("Value of the token")))
    description: str = to_field(String(required=False, metadata=desc("Description of the token")))

    @staticmethod
    def new(description: str) -> 'Token':
        return Token(
            id=str(uuid.uuid4()),
            token_value=str(uuid.uuid4()),
            description=description,
        )

    @staticmethod
    def batch_write(backend: DBInterface, tokens: List['Token']) -> List[str]:
        return backend.batch_insert_obj([
            {
                TYPE_KEY: TypeIDs.TYPE_ID_TOKEN,
                "id": t.id,
                "token_value": t.token_value,
                "description": t.description,
            } for t in tokens
        ])

    @staticmethod
    def batch_read(backend: DBInterface, obj_hashes: List[str]) -> List['Token']:
        raw_token = backend.batch_fetch_obj(obj_hashes)
        return [
            Token(
                id=t["id"],
                token_value=t["token_value"],
                description=t["description"],
            ) for t in raw_token
        ]


token_schema = class_schema(Token)()
