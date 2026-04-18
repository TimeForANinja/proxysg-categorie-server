import json
from dataclasses import dataclass
from typing import List as tList
from marshmallow.fields import List, String
from marshmallow_dataclass import class_schema

from auth.auth_roles import AuthRoles
from util.branch_names import get_user_permission, BranchPermissionFlag, user_branch_name
from util.schema import to_field, desc


@dataclass(kw_only=True)
class AuthUser:
    """
    Represents an authenticated user within the system.
    Holds identifying information and assigned roles.
    """
    username: str = to_field(String(
        required=True,
        metadata=desc('Username of the user')
    ))
    roles: tList[str] = to_field(List(
        String(required=True, metadata=desc('Role name')),
        required=True,
        metadata=desc('List of roles assigned to the user'),
    ))

    def get_permission(self, branch: str) -> BranchPermissionFlag:
        return get_user_permission(self.username, branch)

    def get_branch(self) -> str:
        return user_branch_name(self.username)

    def serialize(self) -> str:
        """
        Serialize the AuthUser object to a JSON string.
        """
        return json.dumps({
            'username': self.username,
            'roles': self.roles
        })

    @staticmethod
    def unserialize(auth_str: str) -> 'AuthUser':
        """
        Create an AuthUser object from a JSON string.
        """
        try:
            auth_data = json.loads(auth_str)
            return AuthUser(
                username=auth_data['username'],
                roles=auth_data.get('roles', [])
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            # Fallback for system or invalid data in legacy code
            return AUTH_USER_SYSTEM


AUTH_USER_SYSTEM = AuthUser(
    username='system',
    roles=[AuthRoles.RO, AuthRoles.RW],
)


auth_user_schema = class_schema(AuthUser)()
