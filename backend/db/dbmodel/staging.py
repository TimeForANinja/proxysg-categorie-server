from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

from auth.auth_user import AuthUser


class ActionType(Enum):
    """Helper class to represent the different types of staged changes."""
    ADD = "add"
    SET_CATS = "set_cats"
    UPDATE = "update"
    DELETE = "delete"

class ActionTable(Enum):
    """Helper class to represent the different tables that can be modified by staged changes."""
    CATEGORY = "category"
    TOKEN = "token"
    URL = "url"


@dataclass(kw_only=True)
class StagedChange:
    """Struct to represent a staged change."""
    action_type: ActionType
    action_table: ActionTable
    auth: AuthUser
    uid: str
    data: Optional[Dict[str, Any]]
    timestamp: int
