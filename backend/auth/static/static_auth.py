from typing import Optional, Tuple

from auth.auth_user import AuthUser, AUTH_ROLES_RO, AUTH_ROLES_RW
from auth.auth_realm import AuthRealmInterface
from auth.util.token import get_shared_token


class StaticAuthRealm(AuthRealmInterface):
    def __init__(self, user: str, password: str):
        self.auth_user = user
        self.auth_password = password
        self.token_file = "static_token.txt"

    def verify_token(self, token: str) -> Optional[AuthUser]:
        if token != get_shared_token(file=self.token_file):
            return None
        return AuthUser(
            username=self.auth_user,
            roles=[
                AUTH_ROLES_RO,
                AUTH_ROLES_RW,
            ]
        )

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        if self.auth_user != username or self.auth_password != password:
            return None

        token = get_shared_token(file=self.token_file)
        user = AuthUser(
            username=self.auth_user,
            roles=[
                AUTH_ROLES_RO,
                AUTH_ROLES_RW,
            ]
        )
        return token, user
