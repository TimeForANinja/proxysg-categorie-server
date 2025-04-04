import os

from apiflask import APIBlueprint
from apiflask.fields import String
from dataclasses import field, dataclass
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from auth import AUTH_TOKEN_KEY, get_token, validate_token
from routes.schemas.generic_output import GenericOutput

auth_bp = APIBlueprint('authentication', __name__)


@dataclass
class JWTHeaderInput:
    jwt_token: str = field(metadata={
        "data_key": AUTH_TOKEN_KEY,
        "required": True,
        "description": "JWT Token for verifying access"
    })


@auth_bp.post("/api/auth/verify")
@auth_bp.input(class_schema(JWTHeaderInput)(), location='headers', arg_name="token")
@auth_bp.output(GenericOutput)
def handle_verify(token: JWTHeaderInput):
    if validate_token(token.jwt_token):
        return {
            "status": 'success',
            "message": 'Login verified successfully',
        }
    else:
        return {
            "status": 'failed',
            "message": 'Invalid token',
        }


@dataclass
class LoginInput:
    username: str = field(metadata={
        "required": True,
        "validate": Length(min=1),
        "description": "Username",
    })
    password: str = field(metadata={
        "required": True,
        "validate": Length(min=1),
        "description": "Password or Token",
    })

class LoginOutput(GenericOutput):
    token = String(required=True, metadata={
        "description": "Token for use with future requests",
    })


@auth_bp.post("/api/auth/login")
@auth_bp.input(class_schema(LoginInput)(), location='json', arg_name="login_input")
@auth_bp.output(LoginOutput)
def handle_auth(login_input: LoginInput):
    auth_type = os.getenv('APP_AUTH_TYPE', 'local')

    if auth_type == 'local':
        auth_user = os.getenv('APP_AUTH_LOCAL_USER', 'admin')
        auth_password = os.getenv('APP_AUTH_LOCAL_PASSWORD', 'nw_admin_2025')
        if login_input.username == auth_user and login_input.password == auth_password:
            response = {
                "status": 'success',
                "message": 'Login successful',
                "token": get_token(),
            }
            return response
    else:
        return {
            "status": 'failed',
            "message": 'Invalid credentials',
        }
