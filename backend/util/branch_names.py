# Name of the "live" Branch
BRANCH_PROD = "b_prod"

def user_branch_name(user: str) -> str:
    """Build the Branch Name for a User-Branch"""
    return f"b_user_{user}"
