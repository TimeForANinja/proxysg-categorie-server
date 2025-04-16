from apiflask import Schema
from apiflask.fields import String, Nested
from dataclasses import field, dataclass
from typing import Optional
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from auth.auth import AUTH_TOKEN_KEY
from auth.auth_user import AuthUser
from routes.schemas.generic_output import GenericOutput

@dataclass
class JWTHeaderInput:
    jwt_token: str = field(metadata={
        'data_key': AUTH_TOKEN_KEY,
        'required': True,
        'description': 'JWT Token for verifying access'
    })


@dataclass
class LoginInput:
    username: str = field(metadata={
        'required': True,
        'validate': Length(min=1),
        'description': 'Username',
    })
    password: str = field(metadata={
        'required': True,
        'validate': Length(min=1),
        'description': 'Password or Token',
    })


class LoginOutputData(Schema):
    token: str = String(required=True, metadata={
        'description': 'Token for use with future requests',
    })
    user: AuthUser = Nested(class_schema(AuthUser)(), required=True, description='User which logged in')


class LoginOutput(GenericOutput):
    data: Optional[LoginOutputData] = Nested(LoginOutputData, required=False, description='Login data, if login was successfully')


class VerifyOutput(GenericOutput):
    data: Optional[AuthUser] = Nested(class_schema(AuthUser)(), required=False, description='User which logged in, if login was successfully')
