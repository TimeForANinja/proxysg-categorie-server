from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Nested
from dataclasses import field, dataclass
from typing import Optional
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from auth.auth import AUTH_TOKEN_KEY
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from routes.schemas.generic_output import GenericOutput


@dataclass
class JWTHeaderInput:
    jwt_token: str = field(metadata={
        "data_key": AUTH_TOKEN_KEY,
        "required": True,
        "description": "JWT Token for verifying access"
    })

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

class LoginOutputData(Schema):
    token: str = String(required=True, metadata={
        "description": "Token for use with future requests",
    })
    user: AuthUser = Nested(class_schema(AuthUser)(), required=True, description="User which logged in")

class LoginOutput(GenericOutput):
    data: Optional[LoginOutputData] = Nested(LoginOutputData, required=False, description="Login data, if login was successfully")

class VerifyOutput(GenericOutput):
    data: Optional[AuthUser] = Nested(class_schema(AuthUser)(), required=False, description="User which logged in, if login was successfully")

def add_auth_bp(app):
    auth_if = get_auth_if(app)
    auth_bp = APIBlueprint('authentication', __name__)

    @auth_bp.post("/api/auth/verify")
    @auth_bp.input(class_schema(JWTHeaderInput)(), location='headers', arg_name="token")
    @auth_bp.output(VerifyOutput)
    def handle_verify(token: JWTHeaderInput):
        user = auth_if.verify_token(token.jwt_token)
        if user is None:
            return {
                "status": 'failed',
                "message": 'Invalid token',
            }
        else:
            return {
                "status": 'success',
                "message": 'Login verified successfully',
                "data": user,
            }


    @auth_bp.post("/api/auth/login")
    @auth_bp.input(class_schema(LoginInput)(), location='json', arg_name="login_input")
    @auth_bp.output(LoginOutput)
    def handle_auth(login_input: LoginInput):
        login = auth_if.check_login(login_input.username, login_input.password)
        if login is None:
            return {
                "status": 'failed',
                "message": 'Invalid credentials',
            }
        else:
            return {
                "status": 'success',
                "message": 'Login successful',
                "data": {
                    "token": login[0],
                    "user": login[1],
                }
            }

    app.register_blueprint(auth_bp)
