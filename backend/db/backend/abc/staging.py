from abc import ABC, abstractmethod
from typing import List

from db.dbmodel.staging import StagedChange


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
