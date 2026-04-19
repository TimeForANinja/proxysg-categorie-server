from dataclasses import dataclass
from apiflask.fields import List, Nested, String
from marshmallow_dataclass import class_schema
from typing import List as tList, Optional

from model.types.category import Category, category_schema
from model.types.shared import Constraint, constraint_schema
from routes.schemas.generic_output import GenericOutput
from routes.types.url import RestConstrainedURL, rest_constrained_url_schema
from util.schema import desc, to_field


@dataclass
class ConstrainedURLListOutput(GenericOutput):
    """Output schema for a single URL-Category mapping"""
    data: List[RestConstrainedURL] = to_field(List(
        Nested(rest_constrained_url_schema),
        required=True,
        metadata=desc("List of URLCategoryMapping"),
    ))

@dataclass
class URLCategoryMappingInput:
    url_id: str = to_field(String(required=True, metadata=desc("ID of the URL of the mapping")))
    constraint: Optional[Constraint] = to_field(Nested(
        constraint_schema,
        required=False,
        metadata=desc("Constraint for the mapping")
    ), default=None)

@dataclass
class ListCategoryOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[Category] = to_field(List(
        Nested(category_schema),
        required=True,
        metadata=desc("List of Categories"),
    ))

constrained_url_list_output_schema = class_schema(ConstrainedURLListOutput)()
url_category_mapping_input_schema = class_schema(URLCategoryMappingInput)()
list_category_output_schema = class_schema(ListCategoryOutput)()


@dataclass
class ChildCategoryMappingInput:
    child_category_id: str = to_field(String(required=True, metadata=desc("ID of the child category")))

@dataclass
class ChildCategoryListOutput(GenericOutput):
    """Output schema for a single URL-Category mapping"""
    data: List[Category] = to_field(List(
        Nested(category_schema),
        required=True,
        metadata=desc("List of all Child Categories"),
    ))

child_category_list_output_schema = class_schema(ChildCategoryListOutput)()
child_category_mapping_input_schema = class_schema(ChildCategoryMappingInput)()


@dataclass
class TokenCategoryMappingInput:
    category_id: str = to_field(String(
        required=True,
        metadata=desc("ID of the Category")
    ))

token_category_mapping_input_schema = class_schema(TokenCategoryMappingInput)()
