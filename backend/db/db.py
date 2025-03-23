from abc import ABC, abstractmethod

from db.categories import CategoriesDBInterface
from db.history import HistoryDBInterface
from db.token_category import TokenCategoryDBInterface
from db.tokens import TokenDBInterface
from db.url_category import UrlCategoryDBInterface
from db.urls import URLDBInterface


class DBInterface(ABC):
    categories: CategoriesDBInterface
    history: HistoryDBInterface
    tokens: TokenDBInterface
    token_categories: TokenCategoryDBInterface
    urls: URLDBInterface
    url_categories: UrlCategoryDBInterface

    @abstractmethod
    def close(self):
        pass
