from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList

from util.schema import desc
from model.types.category import Category, Member, Constraint
from routes.schemas.generic_output import GenericOutput

category_schema = class_schema(Category)()
member_schema = class_schema(Member)()
constraint_schema = class_schema(Constraint)()

class CategoryOutput(GenericOutput):
    """Output schema for a single category"""
    data: Category = Nested(
        category_schema,
        required=True,
        metadata=desc('Category'),
    )

class ListCategoriesOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[Category] = List(
        Nested(category_schema),
        required=True,
        metadata=desc('List of Categories'),
    )
