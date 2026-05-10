from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any, Dict
from apiflask import APIFlask

from auth.auth_schema import AuthMechanism
from auth.auth_user import AuthUser
from auth.jwt.jwt_handler import JWTHandler


class AuthRealmInterface(ABC):
    """
    Interface for authentication providers (realms).
    Every authentication module must implement this interface.
    """

    @abstractmethod
    def get_login_params(self) -> AuthMechanism:
        """
        Return the login parameters for this realm (UI components).
        """
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[AuthUser]:
        """
        Validate a JWT token and return the associated AuthUser.

        :param token: JWT token to validate.
        :return: AuthUser object if valid, else None.
        """
        pass

    @abstractmethod
    def perform_login(self, data: Dict[str, Any]) -> Optional[Tuple[str, AuthUser]]:
        """
        Validate credentials and return a session token and the user object.

        :param data: Generic login data dictionary.
        :return: A tuple of (token, AuthUser) if valid, else None.
        """
        pass


class AuthProviderInterface(ABC):
    """
    Interface for the Plugin API of authentication providers.
    Every provider module must define a class named "AuthProvider" that implements this interface.
    """

    @abstractmethod
    def auth_fits(self, app: APIFlask, auth_type: str) -> bool:
        """
        Return True if this module handles the provided auth_type.
        """
        pass

    @abstractmethod
    def build_auth_realm(self, app: APIFlask, jwt: JWTHandler) -> AuthRealmInterface:
        """
        Factory function to instantiate the provider's realm implementation.
        """
        pass
