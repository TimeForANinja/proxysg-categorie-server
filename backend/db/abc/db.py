from abc import ABC, abstractmethod

from db.abc.category import CategoryDBInterface
from db.abc.history import HistoryDBInterface
from db.abc.staging import StagingDBInterface
from db.abc.sub_category import SubCategoryDBInterface
from db.abc.token_category import TokenCategoryDBInterface
from db.abc.token import TokenDBInterface
from db.abc.url_category import UrlCategoryDBInterface
from db.abc.url import URLDBInterface
from db.abc.task import TaskDBInterface


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
        """Method to trigger any cleanup actions."""
        pass
