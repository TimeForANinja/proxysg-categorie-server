from typing import List
import orjson
from dataclasses import dataclass, field


# Constants
AUTH_ROLES_RO = 'app_admin_ro'
AUTH_ROLES_RW = 'app_admin_rw'


@dataclass(kw_only=True)
class AuthUser:
    """
    Utility Class that holds all data related to a User.
    The data will be used by the API Backend or Frontend,
    and is filled by the Auth Backends.
    """
    username: str = field(metadata={
        'required': True,
        'description': 'Username of the User',
    })
    roles: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of roles assigned to the User',
        }
    )

    def serialize(self) -> str:
        """
        Serialize an AuthUser object to a dictionary that can be converted to JSON.

        :return: A dictionary representation of the AuthUser
        """
        return orjson.dumps({
            'username': self.username,
            'roles': self.roles
        }).decode("utf-8")

    @staticmethod
    def unserialize(auth_str: str) -> 'AuthUser':
        """
        Create an AuthUser object from a dictionary (typically from JSON).

        :param auth_str: A JSON string representing the AuthUser data.
        :return: An AuthUser object
        """
        auth_data = orjson.loads(auth_str)
        return AuthUser(
            username=auth_data['username'],
            roles=auth_data.get('roles', [])
        )


AUTH_USER_SYSTEM = AuthUser(
    username='system',
    roles=[AUTH_ROLES_RO, AUTH_ROLES_RW],
)
