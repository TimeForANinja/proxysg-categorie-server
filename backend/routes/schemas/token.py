from apiflask.fields import List, Nested
from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from typing import List as tList
from dataclasses import field, dataclass

from db.token import Token
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetTokenCategoriesInput:
    """Class for input schema for set categories"""
    categories: tList[str] = field(default_factory=list)


class CreateOrUpdateTokenOutput(GenericOutput):
    """Output schema for create/update token"""
    data: Token = Nested(class_schema(Token)(), required=True, description='Token')


class ListTokenOutput(GenericOutput):
    """Output schema for a list of tokens"""
    data: tList[Token] = List(Nested(class_schema(Token)()), required=True, description='List of Tokens')


class ListTokenCategoriesOutput(GenericOutput):
    """Output schema for listing Categories of a Token"""
    data: tList[str] = List(String, required=True, description='List of Categories')
