from dataclasses import dataclass
from apiflask.fields import List
from typing import List as tList

from marshmallow.fields import String, Nested
from marshmallow_dataclass import class_schema

from model.types.category import category_schema
from util.schema import desc, to_field


@dataclass
class URLMapping:
    url: str = to_field(String(required=True, metadata=desc("URL of the resource")))
    categories: tList[str] = to_field(List(
        Nested(category_schema),
        required=True,
        metadata=desc("Categories (Name) associated with the URL"),
    ))

url_mapping_schema = class_schema(URLMapping)()
