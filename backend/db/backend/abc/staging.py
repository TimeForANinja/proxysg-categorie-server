from abc import ABC, abstractmethod
from typing import List, Optional

from db.backend.abc.util.types import MyTransactionType
from db.dbmodel.staging import StagedChange, ActionTable


class StagingDBInterface(ABC):
    @abstractmethod
    def store_staged_change(self, change: StagedChange):
        """
        Store a staged change in the database.

        :param change: The staged change to store.
        """
        pass

    @abstractmethod
    def store_staged_changes(self, changes: List[StagedChange]):
        """
        Store a list of staged changes in the database.
        Batch Variant of store_staged_change-

        :param changes: The staged changes to store.
        """
        pass

    @abstractmethod
    def get_staged_changes(self, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        """
        Get all staged changes.

        :param session: The database session to use.
        :return: A list of staged changes.
        """
        pass

    @abstractmethod
    def get_staged_changes_by_table(self, table: ActionTable, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        """
        Get all staged changes for a specific table.

        :param table: The table for which to get staged changes.
        :param session: The database session to use.
        :return: A list of staged changes for the given table.
        """
        pass

    @abstractmethod
    def get_staged_changes_by_table_and_id(
        self,
        table: ActionTable,
        obj_id: str,
        session: Optional[MyTransactionType] = None,
    ) -> List[StagedChange]:
        """
        Get all staged changes for a specific table and object ID.

        :param table: The table for which to get staged changes.
        :param obj_id: The object ID for which to get staged changes.
        :param session: The database session to use.
        :return: A list of staged changes for the given table and object ID.
        """
        pass

    @abstractmethod
    def clear_staged_changes(self, before: int = None, session: Optional[MyTransactionType] = None):
        """
        Clear all staged changes.

        :param before: The timestamp before which to clear changes.
        :param session: The database session to use.
        """
        pass
