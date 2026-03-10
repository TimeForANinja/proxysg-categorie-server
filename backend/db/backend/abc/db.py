from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator

from db.backend.abc.category import CategoryDBInterface
from db.backend.abc.git_tree import TagsDBInterface, URLSetDBInterface
from db.backend.abc.task import TaskDBInterface
from db.backend.abc.url import URLDBInterface
from db.backend.abc.util.types import MyTransactionType


class DBInterface(ABC):
    categories: CategoryDBInterface
    urls: URLDBInterface
    tasks: TaskDBInterface
    tags: TagsDBInterface
    url_sets: URLSetDBInterface

    @abstractmethod
    def close(self):
        """
        Method to trigger any cleanup actions.
        This might cause the DBInterface to become unusable.
        """
        pass

    @abstractmethod
    def migrate(self):
        """Method to migrate the database schema."""
        pass

    @contextmanager
    @abstractmethod
    def start_transaction(self) -> Generator[MyTransactionType, None, None]:
        """
        Method to start a transaction.
        The Context Manager returns a transaction object that can be passed to future db calls
        to have them run in the context of the transaction.

        :return: A context manager that can be used to start a transaction.
        """
        pass
