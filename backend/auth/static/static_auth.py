import time
from typing import Optional, Tuple

from auth.auth_user import AuthUser, AUTH_ROLES_RO, AUTH_ROLES_RW
from auth.auth_realm import AuthRealmInterface
from auth.util.jwt_data import TokenData
from auth.util.jwt_handler import JWTHandler


class StaticAuthRealm(AuthRealmInterface):
    def __init__(self, jwt: JWTHandler, user: str, password: str):
        self.jwt = jwt
        self.auth_user = user
        self.auth_password = password

    def verify_token(self, token: str) -> Optional[AuthUser]:
        token_data = self.jwt.verify_token(token)
        if not token_data:
            # Token is invalid or expired
            return None
        return token_data.to_auth_user()

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        if self.auth_user != username or self.auth_password != password:
            return None

        token_data = TokenData(
            username=username,
            roles=[AUTH_ROLES_RO, AUTH_ROLES_RW],
            realm='static',
            date_of_creation=int(time.time())
        )
        token = self.jwt.generate_token(token_data)
        return token, token_data.to_auth_user()
