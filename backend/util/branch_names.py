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


def user_branch_name(user: str) -> str:
    """Build the Branch Name for a User-Branch"""
    return f"b_user_{user}"


def get_user_permission(username: str, branch: str) -> BranchPermissionFlag:
    """Get the Permission for a User-Branch"""
    if branch == user_branch_name(username):
        return BranchPermissionFlag.READ_WRITE
    return BranchPermissionFlag.READ_ONLY
