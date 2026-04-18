import uuid
from dataclasses import dataclass
from apiflask.fields import String
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from util.schema import desc, to_field


@dataclass
class URL:
    id: str = to_field(String(required=True, metadata=desc('ID of the URL')))
    url: str = to_field(String(required=True, metadata=desc('Value of the URL')))

    @staticmethod
    def new(value: str) -> 'URL':
        return URL(
            id=str(uuid.uuid4()),
            url=value
        )

    def write(self, backend: DBInterface) -> str:
        return backend.insert_obj({
            "id": self.id,
            "url": self.url,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'URL':
        raw_url = backend.fetch_obj(obj_hash)
        return URL(
            id=raw_url["id"],
            url=raw_url["url"],
        )


url_schema = class_schema(URL)()
