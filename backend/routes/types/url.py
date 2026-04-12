from dataclasses import dataclass
from apiflask.fields import List, Nested
from typing import List as tList, Optional
from marshmallow_dataclass import class_schema

from model.types.category import category_schema, Category
from model.types.shared import Constraint, constraint_schema
from model.types.url import URL, url_schema
from util.schema import desc, to_field


@dataclass
class RestConstrainedURL:
    url: URL = to_field(Nested(url_schema))
    constraint: Optional[Constraint] = to_field(Nested(
        constraint_schema,
        required=False,
        metadata=desc('Constraint for the URL mapping')
    ), default=None)

rest_constrained_url_schema = class_schema(RestConstrainedURL)()

@dataclass
class RestConstrainedCategory:
    category: Category = to_field(Nested(category_schema))
    constraint: Optional[Constraint] = to_field(Nested(
        constraint_schema,
        required=False,
        metadata=desc('Constraint for the URL mapping')
    ), default=None)

rest_constrained_category_schema = class_schema(RestConstrainedCategory)()


@dataclass
class RestURLDetail:
    url: URL = to_field(
        Nested(url_schema),
    )
    categories: tList[RestConstrainedCategory] = to_field(List(
        Nested(rest_constrained_category_schema),
        required=True,
        metadata=desc("Categories & Constraint associated with the URL"),
    ))

rest_url_detail_schema = class_schema(RestURLDetail)()
