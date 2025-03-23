from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length


@dataclass
class Atomic:
    pass

@dataclass
class History:
    """Helper class to represent a category."""
    id: int = field(metadata={
        "required": True,
        "description": "ID of the category",
    })
    time: int = field(metadata={
        "required": True,
        "description": "Timestamp of the event",
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            "validate": Length(max=255),
            "description": "Description of the category"
        },
    )
    atomics: List[Atomic] = field(default_factory=list)


class HistoryDBInterface(ABC):
    @abstractmethod
    def create_table(self) -> None:
        """
        Create the 'history' table if it doesn't exist.
        """
        pass

    @abstractmethod
    def add_history_event(self, action: str) -> History:
        """
        Add a new history event with the given name

        :param action: The action to be recorded
        :return: The newly created history event
        """
        pass

    @abstractmethod
    def get_history_events(self) -> List[History]:
        """
        Retrieve all history events that are not marked as deleted.

        :return: A list of history events
        """
        pass
