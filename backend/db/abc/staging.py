from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any

from auth.auth_user import AuthUser


class ActionType(Enum):
    """Helper class to represent the different types of staged changes."""
    ADD = "add"
    REMOVE = "remove"
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
    timestamp: int = 0


class StagingDBInterface(ABC):
    @abstractmethod
    def store_staged_change(self, change: StagedChange) -> None:
        """
        Store a staged change in the database.

        :param change: The staged change to store.
        """
        pass

    @abstractmethod
    def get_staged_changes(self) -> List[StagedChange]:
        """
        Get all staged changes.

        :return: A list of staged changes.
        """
        pass

    @abstractmethod
    def clear_staged_changes(self) -> None:
        """
        Clear all staged changes.
        """
        pass
