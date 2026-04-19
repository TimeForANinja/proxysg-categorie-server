# Name of the "live" Branch
import enum

BRANCH_PROD = "b_prod"


class BranchPermissionFlag(str, enum.Enum):
    """
    Permissions for a Branch.
    For now mostly identical to the AuthRoles
    """
    READ_ONLY = "ro"
    READ_WRITE = "rw"

    def __str__(self) -> str:
        """
        this __str__ is required to return the value of the enum instead of its name.
        This is an issue with marshmallow_dataclass (used in the routes),
        which serializes Enums using str() when the field is typed as a string,
        returning the enum name instead of value (e.g., "BranchPermissionFlag.READ_ONLY").
        """
        return self.value


def user_branch_name(user: str) -> str:
    """Build the Branch Name for a User-Branch"""
    return f"b_user_{user}"


def get_user_permission(username: str, branch: str) -> BranchPermissionFlag:
    """Get the Permission for a User-Branch"""
    if branch == user_branch_name(username):
        return BranchPermissionFlag.READ_WRITE
    return BranchPermissionFlag.READ_ONLY
