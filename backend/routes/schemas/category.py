from dataclasses import dataclass
from apiflask.fields import Nested, String, Integer
from marshmallow_dataclass import class_schema

from util.schema import desc, to_field
from model.types.category import Category, category_schema
from routes.schemas.generic_output import GenericOutput


@dataclass
class CategoryCreateInput:
    name: str = to_field(String(
        required=True,
        metadata=desc("Name of the category")
    ))
    description: str = to_field(String(
        required=True,
        metadata=desc("Description of the category")
    ))
    color: int = to_field(Integer(
        required=False,
        metadata=desc("Color of the category")
    ))

@dataclass
class CategoryUpdateInput:
    name: str = to_field(String(
        required=False,
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


category_create_input_schema = class_schema(CategoryCreateInput)()
category_update_input_schema = class_schema(CategoryUpdateInput)()
category_output_schema = class_schema(CategoryOutput)()
