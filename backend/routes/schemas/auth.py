from apiflask import Schema
from apiflask.fields import String, Nested
from dataclasses import field, dataclass
from typing import Optional
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from db.util.schema import desc
from auth.auth import AUTH_TOKEN_KEY
from auth.auth_user import AuthUser, auth_user_schema
from routes.schemas.generic_output import GenericOutput

@dataclass
class JWTHeaderInput:
    jwt_token: str = field(metadata={
        'data_key': AUTH_TOKEN_KEY,
        'required': True,
        **desc('JWT Token for verifying access'),
    })


@dataclass
class LoginInput:
    username: str = field(metadata={
        'required': True,
        'validate': Length(min=1),
        **desc('Username'),
    })
    password: str = field(metadata={
        'required': True,
        'validate': Length(min=1),
        **desc('Password or Token'),
    })


jwt_header_input_schema = class_schema(JWTHeaderInput)()
login_input_schema = class_schema(LoginInput)()


class LoginOutputData(Schema):
    token: str = String(required=True, metadata=desc('Token for use with future requests'))
    user: AuthUser = Nested(
        auth_user_schema,
        required=True,
        metadata=desc('User which logged in'),
    )


class LoginOutput(GenericOutput):
    data: Optional[LoginOutputData] = Nested(
        LoginOutputData,
        required=False,
        metadata=desc('Login data, if login was successfully'),
    )


class VerifyOutput(GenericOutput):
    data: Optional[AuthUser] = Nested(
        auth_user_schema,
        required=False,
        metadata=desc('User which logged in, if login was successfully'),
    )
