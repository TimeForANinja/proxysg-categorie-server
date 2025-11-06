from abc import ABC, abstractmethod
from typing import List, Optional

from db.backend.abc.history import History
from db.dbmodel.history import Atomic


class MiddlewareDBHistory(ABC):
    @abstractmethod
    def get_history_events(self, include_atomics: bool = False) -> List[History]:
        """
        Retrieve all history events that are not marked as deleted.
        Optionally include `atomics` payload for each event.

        :param include_atomics: When True, include the atomics in each history event. Defaults to False.
        :return: A list of history events
        """
        pass

    @abstractmethod
    def get_history_atomics(
        self,
        references_history: Optional[List[str]] = None,
        references_url: Optional[List[str]] = None,
        references_token: Optional[List[str]] = None,
        references_category: Optional[List[str]] = None,
    ) -> List[Atomic]:
        """
        Retrieve a flattened list of all atomic changes, including pending staged changes.

        :param references_history: (opt) List of History IDs to include atomics for
        :param references_url: (opt) List of URL IDs to include atomics for
        :param references_token: (opt) List of Token IDs to include atomics for
        :param references_category: (opt) List of Category IDs to include atomics for
        :return: A list of atomic change items
        """
        pass
