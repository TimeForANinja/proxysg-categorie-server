from dataclasses import dataclass
from apiflask.fields import List, Nested, String
from typing import List as tList
from marshmallow_dataclass import class_schema

from routes.types.token import RestTokenDetail, rest_token_detail_schema
from util.schema import desc, to_field
from model.types.token import Token, token_schema
from routes.schemas.generic_output import GenericOutput


@dataclass
class TokenInput:
    description: str = to_field(String(
        required=True,
        metadata=desc('Description of the token'),
    ))

@dataclass
class TokenOutput(GenericOutput):
    """Output schema for a single token"""
    data: Token = to_field(Nested(
        token_schema,
        required=True,
        metadata=desc('Token'),
    ))

@dataclass
class ListTokenOutput(GenericOutput):
    """Output schema for a list of tokens"""
    data: tList[RestTokenDetail] = to_field(List(
        Nested(rest_token_detail_schema),
        required=True,
        metadata=desc('List of Tokens'),
    ))

@dataclass
class TokenCategoryMappingInput:
    category_id: str = to_field(String(
        required=True,
        metadata=desc('ID of the Category')
    ))


token_output_schema = class_schema(TokenOutput)()
list_token_output_schema = class_schema(ListTokenOutput)()
token_category_mapping_input_schema = class_schema(TokenCategoryMappingInput)()
token_input_schema = class_schema(TokenInput)()
