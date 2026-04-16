import json
from dataclasses import dataclass
from typing import List as tList
from marshmallow.fields import List, String
from marshmallow_dataclass import class_schema

from util.schema import to_field, desc

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
    username: str = to_field(String(
        required=True,
        metadata=desc('Username of the User')
    ))
    roles: tList[str] = to_field(List(
        String(required=True, metadata=desc('Role Value')),
        required=True,
        metadata=desc('List of roles assigned to the User'),
    ))

    def serialize(self) -> str:
        """
        Serialize an AuthUser object to a dictionary that can be converted to JSON.

        :return: A dictionary representation of the AuthUser
        """
        return json.dumps({
            'username': self.username,
            'roles': self.roles
        })

    @staticmethod
    def unserialize(auth_str: str) -> 'AuthUser':
        """
        Create an AuthUser object from a dictionary (typically from JSON).

        :param auth_str: A JSON string representing the AuthUser data.
        :return: An AuthUser object
        """
        auth_data = json.loads(auth_str)
        return AuthUser(
            username=auth_data['username'],
            roles=auth_data.get('roles', [])
        )


AUTH_USER_SYSTEM = AuthUser(
    username='system',
    roles=[AUTH_ROLES_RO, AUTH_ROLES_RW],
)


auth_user_schema = class_schema(AuthUser)()
