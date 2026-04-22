from dataclasses import dataclass
from apiflask.fields import List, Nested, String, Boolean
from typing import List as tList
from marshmallow_dataclass import class_schema

from routes.types.token import RestTokenDetail, rest_token_detail_schema
from util.schema import desc, to_field
from model.types.token import Token, token_schema
from routes.schemas.generic_output import GenericOutput


@dataclass
class ListTokensQuery:
    add_mappings: bool = to_field(Boolean(
        load_default=False,
        metadata=desc("pad with Category mappings"),
    ), default=False)
    add_last_used: bool = to_field(Boolean(
        load_default=False,
        metadata=desc("pad with BC Categories"),
    ), default=False)


@dataclass
class TokenCreateInput:
    description: str = to_field(String(
        required=True,
        metadata=desc("Description of the token"),
    ))

@dataclass
class TokenUpdateInput:
    description: str = to_field(String(
        required=False,
        metadata=desc("Description of the token"),
    ))

@dataclass
class TokenOutput(GenericOutput):
    """Output schema for a single token"""
    data: Token = to_field(Nested(
        token_schema,
        required=True,
        metadata=desc("Token"),
    ))

@dataclass
class ListTokenOutput(GenericOutput):
    """Output schema for a list of tokens"""
    data: tList[RestTokenDetail] = to_field(List(
        Nested(rest_token_detail_schema),
        required=True,
        metadata=desc("List of Tokens"),
    ))


list_tokens_query_schema = class_schema(ListTokensQuery)()
token_output_schema = class_schema(TokenOutput)()
list_token_output_schema = class_schema(ListTokenOutput)()
token_create_input_schema = class_schema(TokenCreateInput)()
token_update_input_schema = class_schema(TokenUpdateInput)()
