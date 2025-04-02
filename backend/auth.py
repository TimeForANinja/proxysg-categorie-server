from apiflask import HTTPTokenAuth
from threading import Lock
from werkzeug.datastructures.auth import Authorization
import secrets


def generate_auth_token(length=64):
    """Generate a secure random authentication token."""
    return secrets.token_hex(length)


# Constants
AUTH_TOKEN_KEY = "jwt-token"
AUTH_ROLES_RO = "pxy_admin_ro"
AUTH_ROLES_RW = "pxy_admin_rw"
AUTH_DEFAULT_TOKEN = generate_auth_token()

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
    return token == AUTH_DEFAULT_TOKEN

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

