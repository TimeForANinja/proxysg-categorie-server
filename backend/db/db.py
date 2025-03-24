from abc import ABC, abstractmethod

from db.category import CategoryDBInterface
from db.history import HistoryDBInterface
from db.token_category import TokenCategoryDBInterface
from db.token import TokenDBInterface
from db.url_category import UrlCategoryDBInterface
from db.url import URLDBInterface


class DBInterface(ABC):
    categories: CategoryDBInterface
    history: HistoryDBInterface
    tokens: TokenDBInterface
    token_categories: TokenCategoryDBInterface
    urls: URLDBInterface
    url_categories: UrlCategoryDBInterface

    @abstractmethod
    def close(self):
        pass
