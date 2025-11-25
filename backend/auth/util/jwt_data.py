from typing import List, Dict, Any
from dataclasses import dataclass

from auth.auth_user import AuthUser


@dataclass
class TokenData:
    """
    This class represents all data stored in a JWT token.
    """
    # TODO: use AuthUser instead of username and roles
    username: str
    roles: List[str]
    realm: str
    date_of_creation: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert the TokenData object to a dictionary."""
        return {
            'username': self.username,
            'roles': self.roles,
            'realm': self.realm,
            'date_of_creation': self.date_of_creation
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TokenData':
        """Create a TokenData object from a dictionary."""
        return TokenData(
            username=data.get('username'),
            roles=data.get('roles', []),
            realm=data.get('realm'),
            date_of_creation=data.get('date_of_creation'),
        )

    def to_auth_user(self) -> AuthUser:
        """Convert the TokenData object to an AuthUser object."""
        return AuthUser(
            username=self.username,
            roles=self.roles,
        )
