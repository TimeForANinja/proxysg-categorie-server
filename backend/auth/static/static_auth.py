import time
from typing import Optional, Tuple
from flask import request

from auth.auth_user import AuthUser, AUTH_ROLES_RO, AUTH_ROLES_RW
from auth.auth_realm import AuthRealmInterface
from auth.util.jwt_data import TokenData
from auth.util.jwt_handler import JWTHandler
from log import log_error, log_info


class StaticAuthRealm(AuthRealmInterface):
    jwt: JWTHandler
    auth_user: str
    auth_password: str

    def __init__(self, jwt: JWTHandler, user: str, password: str):
        self.jwt = jwt
        self.auth_user = user
        self.auth_password = password

    def verify_token(self, token: str) -> Optional[AuthUser]:
        token_data = self.jwt.verify_token(token)
        if not token_data:
            # Token is invalid or expired
            log_error( 'AUTH', f'Authentication error: SRC_IP:{request.remote_addr}')
            return None
        log_info( 'AUTH', f'Auth successfully: SRC_IP:{request.remote_addr}', token_data)
        return token_data.to_auth_user()

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        if self.auth_user != username or self.auth_password != password:
            log_error( 'AUTH', f'Authentication error: SRC_IP:{request.remote_addr}', { 'username': username })
            return None

        log_info('AUTH', f'Auth successfully: SRC_IP:{request.remote_addr}', { 'username': username })
        token_data = TokenData(
            username=username,
            roles=[AUTH_ROLES_RO, AUTH_ROLES_RW],
            realm='static',
            date_of_creation=int(time.time())
        )
        token = self.jwt.generate_token(token_data)
        return token, token_data.to_auth_user()
