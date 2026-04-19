from typing import Optional, List, Tuple
from apiflask import HTTPTokenAuth

from auth.auth_realm import AuthRealmInterface
from auth.auth_user import AuthUser


# HTTP Header name for the Auth token
AUTH_TOKEN_KEY = "jwt-token"


class AuthHandler:
    """
    Coordinator for multiple authentication realms.
    Integrates with APIFlask's HTTPTokenAuth to provide authentication and authorization.
    """
    # vars
    realms: List[AuthRealmInterface]

    def __init__(self, realms: List[AuthRealmInterface]):
        self.realms = realms

    def verify_token(self, token: str) -> Optional[AuthUser]:
        """
        Validate if the provided token is valid by checking it against all configured realms.

        :param token: JWT token to validate.
        :return: AuthUser object if the token is valid in any realm, else None.
        """
        for realm in self.realms:
            user = realm.verify_token(token)
            if user is not None:
                return user
        return None

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        """
        Check a login attempt against all configured realms.
        Returns the first successful match.

        :param username: Username.
        :param password: Password.
        :return: A tuple of (token, AuthUser) if successful, else None.
        """
        for realm in self.realms:
            result = realm.check_login(username, password)
            if result is not None:
                return result
        return None

    auth = None
    def get_auth(self) -> HTTPTokenAuth:
        """
        Build the Auth object requested by APIFlask.
        Implemented as a Singleton.
        """
        if self.auth is None:
            self.auth = _build_flask_auth(self)
        return self.auth


def _build_flask_auth(auth_if: AuthHandler):
    """
    Utility class to build the HTTPTokenAuth object.
    The object is required to use the APIFlask-integrated authentication mechanism.
    This is a simple process, since the AuthHandler defines all methods required.
    """
    auth = HTTPTokenAuth(
        scheme="Bearer",
        header=AUTH_TOKEN_KEY,
    )

    @auth.get_user_roles
    def get_user_roles(user: AuthUser) -> List[str]:
        """
        retrieve user roles from an Authorization object.

        :param user: Authorization object
        :return: list of roles
        """
        return user.roles

    @auth.verify_token
    def verify_token(token: str) -> Optional[AuthUser]:
        """
        Validate a User and the parsed User-Object that can later be used

        :param token: The token to be validated
        :return: AuthUser
        """
        return auth_if.verify_token(token)

    return auth
