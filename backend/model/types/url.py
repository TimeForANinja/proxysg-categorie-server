import uuid
from dataclasses import dataclass
from typing import List

from apiflask.fields import String
from marshmallow_dataclass import class_schema

from db.abc.constants import TYPE_KEY, TypeIDs
from db.abc.db import DBInterface
from util.schema import desc, to_field


@dataclass
class URL:
    id: str = to_field(String(required=True, metadata=desc("ID of the URL")))
    url: str = to_field(String(required=True, metadata=desc("Value of the URL")))
    description: str = to_field(String(required=True, metadata=desc("Description of the URL")))

    @staticmethod
    def new(value: str, description: str) -> 'URL':
        return URL(
            id=str(uuid.uuid4()),
            url=value,
            description=description,
        )

    @staticmethod
    def batch_write(backend: DBInterface, urls: List['URL']) -> List[str]:
        return backend.batch_insert_obj([
            {
                TYPE_KEY: TypeIDs.TYPE_ID_URL,
                "id": u.id,
                "url": u.url,
                "description": u.description,
            } for u in urls
        ])

    @staticmethod
    def batch_read(backend: DBInterface, obj_hashes: List[str]) -> List['URL']:
        raw_urls = backend.batch_fetch_obj(obj_hashes)
        return [
            URL(
                id=u["id"],
                url=u["url"],
                description=u["description"],
            ) for u in raw_urls
        ]


url_schema = class_schema(URL)()
