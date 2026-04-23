import enum


# Constants
class AuthRoles(str, enum.Enum):
    """
    Roles that can be assigned to users.
    """
    RO = "app_admin_ro"
    RW = "app_admin_rw"
    NONE = "app_unauthenticated"
