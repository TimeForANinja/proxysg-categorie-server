from abc import ABC, abstractmethod
from typing import Optional, Tuple

from auth.auth_user import AuthUser


class AuthRealmInterface(ABC):
    """
    This interface defines all methods required for:
    * API Auth calls like login
    * API restrictions based on the apiflask HTTPTokenAuth
    """

    @abstractmethod
    def verify_token(self, token: str) -> Optional[AuthUser]:
        """
        Validate if the provided token is valid

        Overwrite for the flask.HTTPTokenAuth

        :param token: Token to validate
        :return: AuthUser object if valid, else None
        """
        pass

    @abstractmethod
    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        """
        Check a login attempt

        Custom function to resolve User to Token, which will then be used for API calls

        :param username: Username
        :param password: Password
        :return: Token if valid, else None
        """
        pass
