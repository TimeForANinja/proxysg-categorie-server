from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList
from dataclasses import field, dataclass

from db.util.schema import desc
from db.dbmodel.token import Token, token_schema
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetTokenCategoriesInput:
    """Class for input schema for set categories"""
    categories: tList[str] = field(default_factory=list)


set_token_categories_input_schema = class_schema(SetTokenCategoriesInput)()


class CreateOrUpdateTokenOutput(GenericOutput):
    """Output schema for create/update token"""
    data: Token = Nested(token_schema, required=True, metadata=desc('Token'))


class ListTokenOutput(GenericOutput):
    """Output schema for a list of tokens"""
    data: tList[Token] = List(Nested(token_schema), required=True, metadata=desc('List of Tokens'))


class ListTokenCategoriesOutput(GenericOutput):
    """Output schema for listing Categories of a Token"""
    data: tList[str] = List(String, required=True, metadata=desc('List of Categories'))
