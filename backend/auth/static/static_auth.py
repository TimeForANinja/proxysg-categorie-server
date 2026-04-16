import time
from typing import Optional, Tuple
from flask import request

from auth.auth_user import AuthUser, AUTH_ROLES_RO, AUTH_ROLES_RW
from auth.auth_realm import AuthRealmInterface
from auth.util.jwt_data import TokenData
from auth.util.jwt_handler import JWTHandler
from log import log_error, log_info
from apiflask import APIFlask


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


# Plugin API
def auth_fits(app: APIFlask, auth_type: str) -> bool:
    """
    Return True if this module handles the provided auth_type entry from AUTH.ORDER.
    """
    return auth_type.strip().lower() == 'local'


def build_auth_realm(app: APIFlask, jwt: JWTHandler) -> AuthRealmInterface:
    """
    Build and return the StaticAuthRealm using values from app.config.
    """
    local_cfg = app.config.get('AUTH', {}).get('LOCAL', {})
    static_user = local_cfg.get('USER', 'admin')
    static_password = local_cfg.get('PASSWORD', 'nw_admin_2025')
    log_info('AUTH', 'Adding Static Realm', {'user': static_user})
    return StaticAuthRealm(jwt, static_user, static_password)
