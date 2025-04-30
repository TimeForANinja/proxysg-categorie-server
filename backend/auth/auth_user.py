from typing import List
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


AUTH_USER_SYSTEM = AuthUser(
    username='system',
    roles=[AUTH_ROLES_RO, AUTH_ROLES_RW],
)
