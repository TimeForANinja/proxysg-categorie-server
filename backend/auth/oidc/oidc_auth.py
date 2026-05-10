from typing import Optional, Tuple
from apiflask import APIFlask
from flask import redirect

from auth.auth_schema import AuthMechanism, AuthUIComponent
from auth.auth_user import AuthUser
from auth.auth_realm import AuthRealmInterface, AuthProviderInterface
from auth.jwt.jwt_handler import JWTHandler

ROUTE_PREFIX = "/api/auth/realm/oidc"


class OIDCAuthRealm(AuthRealmInterface):
    def __init__(self, jwt: JWTHandler):
        self.jwt = jwt

    def get_login_params(self) -> AuthMechanism:
        return AuthMechanism(
            type="oidc",
            label="OIDC Login",
            ui=[
                AuthUIComponent(
                    type="button",
                    label="Login with OIDC",
                    location=f"{ROUTE_PREFIX}/login"
                ),
            ]
        )

    def verify_token(self, token: str) -> Optional[AuthUser]:
        # TODO: implement
        pass

    def perform_login(self, data: dict) -> Optional[Tuple[str, AuthUser]]:
        return None


def _add_oidc_routes(app: APIFlask):
    @app.get(f"{ROUTE_PREFIX}/login")
    @app.doc(summary="Login", description="Login using OIDC", tags=["Auth"], responses={
        302: {"description": "Redirect to OIDC provider for login"},
    })
    def login():
        # TODO: implement
        return redirect("/")

    @app.post(f"{ROUTE_PREFIX}/callback")
    @app.doc(summary="Login", description="Login using OIDC", tags=["Auth"], responses={
        302: {"description": "Redirect to Root-Page if successfully, or back to Login if not"},
    })
    def callback():
        # TODO: implement
        return redirect("/")


class AuthProvider(AuthProviderInterface):
    def auth_fits(self, app: APIFlask, auth_type: str) -> bool:
        return auth_type == "oidc"

    def build_auth_realm(self, app: APIFlask, jwt: JWTHandler) -> AuthRealmInterface:
        _add_oidc_routes(app)
        return OIDCAuthRealm(jwt)
