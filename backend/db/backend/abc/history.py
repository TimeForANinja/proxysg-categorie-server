from abc import ABC, abstractmethod
from typing import Optional, List

from auth.auth_user import AuthUser
from db.backend.abc.util.types import MyTransactionType
from db.dbmodel.history import Atomic, History


class HistoryDBInterface(ABC):
    @abstractmethod
    def add_history_event(
        self,
        action: str,
        user: AuthUser,
        ref_token: List[str],
        ref_url: List[str],
        ref_category: List[str],
        atomics: Optional[List[Atomic]] = None,
        session: Optional[MyTransactionType] = None,
    ) -> History:
        """
        Add a new history event with the given name

        :param action: The action to be recorded
        :param user: The user who performed the action
        :param ref_token: List of token IDs referenced by the action
        :param ref_url: List of URL IDs referenced by the action
        :param ref_category: List of category IDs referenced by the action
        :param atomics: Optional list of atomic changes
        :param session: Optional database session to use
        :return: The newly created history event
        """
        pass

    @abstractmethod
    def get_history_events(self, include_atomics: bool = False) -> List[History]:
        """
        Retrieve all history events that are not marked as deleted.

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
    ):
        """
        Retrieve a flattened list of all atomic changes.

        :param references_history: (opt) List of History IDs to include atomics for
        :param references_url: (opt) List of URL IDs to include atomics for
        :param references_token: (opt) List of Token IDs to include atomics for
        :param references_category: (opt) List of Category IDs to include atomics for
        :return: A list of atomic change items
        """
        pass
