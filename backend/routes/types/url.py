from dataclasses import dataclass
from apiflask.fields import List, Nested
from typing import List as tList, Optional
from marshmallow.fields import String
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
        metadata=desc("Constraint for the URL mapping")
    ), default=None)

rest_constrained_url_schema = class_schema(RestConstrainedURL)()

@dataclass
class RestConstrainedCategory:
    category: Category = to_field(Nested(category_schema))
    constraint: Optional[Constraint] = to_field(Nested(
        constraint_schema,
        required=False,
        metadata=desc("Constraint for the URL mapping")
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


@dataclass
class RestTestResult:
    input: str = to_field(String(
        required=True,
        metadata=desc("Raw Input URL")
    ))
    normalized_input: str = to_field(String(
        required=True,
        metadata=desc("Cleaned URL used for matching")
    ))
    matched_url: str = to_field(String(
        required=True,
        metadata=desc("The best-fit URL found in the DB")
    ))
    local_categories: tList[str] = to_field(List(
        String(required=True, metadata=desc("Category Name")),
        required=False,
        metadata=desc("List of all Categories matched for the URL"),
    ))
    bc_categories: tList[str] = to_field(List(
        String(required=True, metadata=desc("Bluecoat Category")),
        required=False,
        metadata=desc("List of all Bluecoat Categories matched for the URL"),
    ))

rest_test_result_schema = class_schema(RestTestResult)()
