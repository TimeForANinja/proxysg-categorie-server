from dataclasses import dataclass
from typing import Optional, List as tList, Dict as tDict
from apiflask.fields import String, Nested, List, Dict
from marshmallow_dataclass import class_schema

from auth.auth import AUTH_TOKEN_KEY
from auth.auth_schema import AuthMechanism, auth_mechanism_schema
from auth.auth_user import AuthUser, auth_user_schema
from routes.schemas.generic_output import GenericOutput
from util.schema import to_field, desc


@dataclass
class JWTHeaderInput:
    jwt_token: str = to_field(String(
        required=True,
        data_key=AUTH_TOKEN_KEY,
        metadata=desc("Value of the JWT Token")
    ))


@dataclass
class LoginInput:
    data: tDict = to_field(Dict(
        required=True,
        metadata=desc("Generic login data dictionary")
    ))


@dataclass
class LoginOutputData:
    token: str = to_field(String(required=True, metadata=desc("Token for use with future requests")))
    user: AuthUser = to_field(Nested(
        auth_user_schema,
        required=True,
        metadata=desc("User which logged in")
    ))

login_output_data_schema = class_schema(LoginOutputData)()


@dataclass
class LoginOutput(GenericOutput):
    data: Optional[LoginOutputData] = to_field(Nested(
        login_output_data_schema,
        required=False,
        metadata=desc("Login data, if login was successfully")
    ), default=None)


@dataclass
class VerifyOutput(GenericOutput):
    data: Optional[AuthUser] = to_field(Nested(
        login_output_data_schema,
        required=False,
        metadata=desc("User which logged in, if login was successfully")
    ), default=None)


jwt_header_schema = class_schema(JWTHeaderInput)()
login_input_schema = class_schema(LoginInput)()
verify_output_schema = class_schema(VerifyOutput)()
login_output_schema = class_schema(LoginOutput)()


@dataclass
class AuthMechanismsOutput(GenericOutput):
    data: tList[AuthMechanism] = to_field(List(
        Nested(auth_mechanism_schema),
        required=True,
        metadata=desc("List of supported auth mechanisms with UI details"),
    ))


auth_mechanisms_output_schema = class_schema(AuthMechanismsOutput)()
