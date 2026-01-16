from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList
from dataclasses import field, dataclass

from db.util.schema import desc
from db.dbmodel.category import Category, category_schema
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetSubCategoriesInput:
    """Class for input schema for set subcategories"""
    categories: tList[str] = field(default_factory=list)


set_sub_categories_input_schema = class_schema(SetSubCategoriesInput)()


class CreateOrUpdateCategoryOutput(GenericOutput):
    """Output schema for create/update category"""
    data: Category = Nested(
        category_schema,
        required=True,
        metadata=desc('Category'),
    )


class ListCategoriesResponseOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[Category] = List(
        Nested(category_schema),
        required=True,
        metadata=desc('List of Categories'),
    )


class ListSubCategoriesOutput(GenericOutput):
    """Output schema for listing Sub-Categories of a Category"""
    data: tList[str] = List(
        String,
        required=True,
        metadata=desc('List of Sub-Categories'),
    )
