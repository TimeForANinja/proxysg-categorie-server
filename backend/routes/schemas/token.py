from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList

from util.schema import desc
from model.types.token import Token
from routes.schemas.generic_output import GenericOutput

token_schema = class_schema(Token)()

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
