import time
from typing import Optional, Tuple
from flask import request
from apiflask import APIFlask

from auth.auth_roles import AuthRoles
from util.log import log_error, log_info

from auth.auth_user import AuthUser
from auth.auth_realm import AuthRealmInterface, AuthProviderInterface
from auth.jwt.jwt_data import TokenData
from auth.jwt.jwt_handler import JWTHandler


class StaticAuthRealm(AuthRealmInterface):
    jwt: JWTHandler
    auth_user: str
    auth_password: str

    def __init__(self, jwt: JWTHandler, user: str, password: str):
        self.jwt = jwt
        self.auth_user = user
        self.auth_password = password

    def verify_token(self, token: str) -> Optional[AuthUser]:
        """
        Validate the provided JWT token.
        """
        token_data = self.jwt.verify_token(token)
        if not token_data:
            # Token is invalid or expired
            log_error('AUTH', f'Authentication failed: Invalid or expired token from SRC_IP:{request.remote_addr}')
            return None

        auth_user = token_data.to_auth_user()
        log_info('AUTH', f'Authentication successful: User {token_data.user.username} from SRC_IP:{request.remote_addr}', auth_user)
        return auth_user

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        """
        Check credentials against the static configuration.
        """
        if self.auth_user != username or self.auth_password != password:
            log_error('AUTH', f'Login failed: Invalid credentials for user {username} from SRC_IP:{request.remote_addr}')
            return None

        auth_user = AuthUser(
            username=username,
            roles=[AuthRoles.RO, AuthRoles.RW]
        )
        log_info('AUTH', f'Login successful: User {username} from SRC_IP:{request.remote_addr}', auth_user)
        token_data = TokenData(
            user=auth_user,
            realm='static',
            date_of_creation=int(time.time())
        )
        token = self.jwt.generate_token(token_data)
        return token, auth_user


class AuthProvider(AuthProviderInterface):
    """
    Static Authentication Provider plugin.
    Handles 'local' auth types and builds the StaticAuthRealm.
    """

    def auth_fits(self, app: APIFlask, auth_type: str) -> bool:
        """
        Return True if this module handles the provided auth_type entry from AUTH.ORDER.
        """
        return auth_type == 'local'

    def build_auth_realm(self, app: APIFlask, jwt: JWTHandler) -> AuthRealmInterface:
        """
        Build and return the StaticAuthRealm using values from app.config.
        """
        local_cfg = app.config.get('AUTH', {}).get('LOCAL', {})
        static_user = local_cfg.get('USER', 'admin')
        static_password = local_cfg.get('PASSWORD', 'nw_admin_2025')
        log_info('AUTH', 'Adding Static Realm', {'user': static_user})
        return StaticAuthRealm(jwt, static_user, static_password)
