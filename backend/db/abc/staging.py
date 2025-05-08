from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


class ActionType(Enum):
    """Helper class to represent the different types of staged changes."""
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    SET_CATEGORIES = "set_categories"

class ActionTable(Enum):
    """Helper class to represent the different tables that can be modified by staged changes."""
    CATEGORIES = "categories"
    TOKENS = "tokens"
    URLS = "urls"


@dataclass(kw_only=True)
class MutableStagedChange:
    """Struct to represent the mutable parts of a staged change."""
    action: ActionType
    user: str
    table: ActionTable
    entity_id: str
    data: dict

@dataclass(kw_only=True)
class StagedChange(MutableStagedChange):
    """Struct to represent a staged change."""
    id: str
    action: ActionType
    user: str
    time: int
    table: ActionTable
    entity_id: str
    data: dict


class StagingDBInterface(ABC):
    @abstractmethod
    def store_staged_change(self, change: MutableStagedChange) -> None:
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
