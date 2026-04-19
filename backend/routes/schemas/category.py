from dataclasses import dataclass
from apiflask.fields import List, Nested, String, Integer
from typing import List as tList, Optional
from marshmallow_dataclass import class_schema

from model.types.shared import Constraint, constraint_schema
from routes.types.url import rest_constrained_url_schema, RestConstrainedURL
from util.schema import desc, to_field
from model.types.category import Category, category_schema
from routes.schemas.generic_output import GenericOutput


@dataclass
class URLCategoryMappingInput:
    url_id: str = to_field(String(required=True, metadata=desc("ID of the URL of the mapping")))
    constraint: Optional[Constraint] = to_field(Nested(
        constraint_schema,
        required=False,
        metadata=desc("Constraint for the mapping")
    ), default=None)

@dataclass
class ConstrainedURLListOutput(GenericOutput):
    """Output schema for a single URL-Category mapping"""
    data: List[RestConstrainedURL] = to_field(List(
        Nested(rest_constrained_url_schema),
        required=True,
        metadata=desc("List of URLCategoryMapping"),
    ))

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

@dataclass
class CategoryInput:
    name: str = to_field(String(
        required=True,
        metadata=desc("Name of the category")
    ))
    description: str = to_field(String(
        required=False,
        metadata=desc("Description of the category")
    ))
    color: int = to_field(Integer(
        required=False,
        metadata=desc("Color of the category")
    ))

@dataclass
class CategoryOutput(GenericOutput):
    """Output schema for a single category"""
    data: Category = to_field(Nested(
        category_schema,
        required=True,
        metadata=desc("Category"),
    ))

@dataclass
class ListCategoryOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[Category] = to_field(List(
        Nested(category_schema),
        required=True,
        metadata=desc("List of Categories"),
    ))


url_category_mapping_input_schema = class_schema(URLCategoryMappingInput)()
constrained_url_list_output_schema = class_schema(ConstrainedURLListOutput)()
child_category_mapping_input_schema = class_schema(ChildCategoryMappingInput)()
child_category_list_output_schema = class_schema(ChildCategoryListOutput)()
category_input_schema = class_schema(CategoryInput)()
category_output_schema = class_schema(CategoryOutput)()
list_category_output_schema = class_schema(ListCategoryOutput)()
