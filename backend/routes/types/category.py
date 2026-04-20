from dataclasses import dataclass
from apiflask.fields import List, Nested
from typing import List as tList
from marshmallow_dataclass import class_schema

from model.types.category import Category, category_schema
from util.schema import to_field, desc


@dataclass
class RestCategoryDetail:
    category: Category = to_field(Nested(category_schema))
    children: tList[Category] = to_field(List(
        Nested(category_schema),
        required=True,
        metadata=desc('Categories associated as "Children" with the URL'),
    ))

rest_category_detail_schema = class_schema(RestCategoryDetail)()
