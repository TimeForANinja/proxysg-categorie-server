from dataclasses import dataclass
from apiflask.fields import List, Nested, Integer
from typing import List as tList
from marshmallow_dataclass import class_schema

from model.types.category import category_schema, Category
from model.types.token import Token, token_schema
from util.schema import desc, to_field


@dataclass
class RestTokenDetail:
    token: Token = to_field(
        Nested(token_schema)
    )
    categories: tList[Category] = to_field(List(
        Nested(category_schema),
        required=True,
        metadata=desc("Categories associated with the URL"),
    ))
    last_used: int = to_field(Integer(
        required=True,
        metadata=desc("Last-Used timestamp, or -1 if never used")
    ))

rest_token_detail_schema = class_schema(RestTokenDetail)()
