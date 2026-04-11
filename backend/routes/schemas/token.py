from dataclasses import dataclass

from apiflask.fields import List, Nested, String
from typing import List as tList

from marshmallow_dataclass import class_schema

from model.types.category import category_schema
from util.schema import desc, to_field
from model.types.token import Token, token_schema
from routes.schemas.generic_output import GenericOutput

@dataclass
class TokenInput:
    description: str = to_field(String(
        required=True,
        metadata=desc('Description of the token'),
    ))

class TokenCategoryOutput(GenericOutput):
    """Output schema for token category association"""
    data: tList[dict] = List(
        Nested(category_schema),
        required=True,
        metadata=desc('List of Categories for a specific Token'),
    )

class TokenOutput(GenericOutput):
    """Output schema for a single token"""
    data: Token = Nested(
        token_schema,
        required=True,
        metadata=desc('Token'),
    )

class ListTokensOutput(GenericOutput):
    """Output schema for a list of tokens"""
    data: tList[Token] = List(
        Nested(token_schema),
        required=True,
        metadata=desc('List of Tokens'),
    )

@dataclass
class CategoryMemberInput:
    category: str = to_field(String(required=True, metadata=desc('ID of the Category')))

category_member_input_schema = class_schema(CategoryMemberInput)()
token_input_schema = class_schema(TokenInput)()
