from typing import Dict, Any, Optional
from dataclasses import dataclass

from auth.auth_user import AuthUser


@dataclass
class TokenData:
    """
    Represents the payload data stored within a JWT token.
    """
    user: AuthUser
    realm: str
    date_of_creation: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the TokenData object to a dictionary for JWT encoding.
        """
        return {
            "user": self.user.serialize(),
            "realm": self.realm,
            "date_of_creation": self.date_of_creation
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Optional['TokenData']:
        """
        Create a TokenData object from a dictionary.
        Returns None if required fields are missing.
        """
        try:
            return TokenData(
                user=AuthUser.unserialize(data["user"]),
                realm=data["realm"],
                date_of_creation=data["date_of_creation"],
            )
        except (KeyError, TypeError):
            return None

    def to_auth_user(self) -> AuthUser:
        """
        Convert the TokenData object to an AuthUser object for application use.
        """
        return self.user
