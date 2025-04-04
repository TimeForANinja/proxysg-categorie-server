import os
import secrets
from apiflask import HTTPTokenAuth
from threading import Lock
from werkzeug.datastructures.auth import Authorization


def generate_auth_token(length=64):
    """Generate a secure random authentication token."""
    return secrets.token_hex(length)


# Constants
AUTH_TOKEN_KEY = "jwt-token"
AUTH_ROLES_RO = "pxy_admin_ro"
AUTH_ROLES_RW = "pxy_admin_rw"

token_file = "/tmp/auth_token.txt"
def get_token() -> str:
    """
    This method returns the current authentication token.

    Unfortunately writing to a tmp file is currently the best way to achieve this.
    Adding to flask g like done for the db_singleton does not work, since it's not thread safe.
    An alternative would be to use redis, but this would be overkill to setup just for this use-case.
    """
    if not os.path.exists(token_file):
        token = generate_auth_token()
        with open(token_file, "w") as f:
            f.write(token)
    else:
        with open(token_file, "r") as f:
            token = f.read().strip()

    return token

def get_auth():
    return AuthSingleton().get_auth()

def _build_auth():
    auth = HTTPTokenAuth(
        scheme='Bearer',
        header=AUTH_TOKEN_KEY,
    )

    @auth.get_user_roles
    def get_user_roles(user: Authorization):
        return [AUTH_ROLES_RO, AUTH_ROLES_RW]

    @auth.verify_token
    def verify_token(token: str) -> bool:
        return validate_token(token)

    return auth

def validate_token(token: str) -> bool:
    return token == get_token()

class AuthSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AuthSingleton, cls).__new__(cls)
                cls._instance._auth = _build_auth()
            return cls._instance

    def get_auth(self):
        return self._auth

