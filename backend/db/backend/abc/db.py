from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator

from db.backend.abc.category import CategoryDBInterface
from db.backend.abc.history import HistoryDBInterface
from db.backend.abc.staging import StagingDBInterface
from db.backend.abc.sub_category import SubCategoryDBInterface
from db.backend.abc.task import TaskDBInterface
from db.backend.abc.token import TokenDBInterface
from db.backend.abc.token_category import TokenCategoryDBInterface
from db.backend.abc.url import URLDBInterface
from db.backend.abc.url_category import UrlCategoryDBInterface
from db.backend.abc.util.types import MyTransactionType


class DBInterface(ABC):
    categories: CategoryDBInterface
    sub_categories: SubCategoryDBInterface
    history: HistoryDBInterface
    tokens: TokenDBInterface
    token_categories: TokenCategoryDBInterface
    urls: URLDBInterface
    url_categories: UrlCategoryDBInterface
    tasks: TaskDBInterface
    staging: StagingDBInterface

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
        pass
