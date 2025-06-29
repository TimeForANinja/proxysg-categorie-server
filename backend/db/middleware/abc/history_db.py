from abc import ABC, abstractmethod
from typing import List

from db.backend.abc.history import History


class MiddlewareDBHistory(ABC):
    @abstractmethod
    def get_history_events(self) -> List[History]:
        """
        Retrieve all history events that are not marked as deleted.

        :return: A list of history events
        """
        pass
