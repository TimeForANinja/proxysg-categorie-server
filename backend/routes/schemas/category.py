from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList
from dataclasses import field, dataclass

from db.dbmodel.category import Category
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetSubCategoriesInput:
    """Class for input schema for set subcategories"""
    categories: tList[str] = field(default_factory=list)


class CreateOrUpdateCategoryOutput(GenericOutput):
    """Output schema for create/update category"""
    data: Category = Nested(class_schema(Category)(), required=True, description='Category')


class ListCategoriesResponseOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[Category] = List(Nested(class_schema(Category)()), required=True, description='List of Categories')


class ListSubCategoriesOutput(GenericOutput):
    """Output schema for listing Sub-Categories of a Category"""
    data: tList[str] = List(String, required=True, description='List of Sub-Categories')
