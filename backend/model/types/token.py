import uuid
from dataclasses import dataclass
from marshmallow.fields import String
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from util.schema import desc, to_field


@dataclass
class Token:
    id: str = to_field(String(required=True, metadata=desc('ID of the token')))
    token_value: str = to_field(String(required=True, metadata=desc('Value of the token')))
    description: str = to_field(String(required=False, metadata=desc('Description of the token')))

    @staticmethod
    def new(description: str) -> 'Token':
        return Token(
            id=str(uuid.uuid4()),
            token_value=str(uuid.uuid4()),
            description=description,
        )

    def write(self, backend: DBInterface) -> str:
        return backend.insert_obj({
            "id": self.id,
            "token_value": self.token_value,
            "description": self.description,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Token':
        raw_token = backend.fetch_obj(obj_hash)
        return Token(
            id=raw_token["id"],
            token_value=raw_token["token_value"],
            description=raw_token["description"],
        )


token_schema = class_schema(Token)()
