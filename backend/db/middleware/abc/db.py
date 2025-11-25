from abc import ABC, abstractmethod

from db.middleware.abc.category_db import MiddlewareDBCategory
from db.middleware.abc.history_db import MiddlewareDBHistory
from db.middleware.abc.sub_category_db import MiddlewareDBSubCategory
from db.middleware.abc.task_db import MiddlewareDBTask
from db.middleware.abc.token_category_db import MiddlewareDBTokenCategory
from db.middleware.abc.token_db import MiddlewareDBToken
from db.middleware.abc.url_category_db import MiddlewareDBURLCategory
from db.middleware.abc.url_db import MiddlewareDBURL


class MiddlewareDB(ABC):
    categories: MiddlewareDBCategory
    sub_categories: MiddlewareDBSubCategory
    history: MiddlewareDBHistory
    tokens: MiddlewareDBToken
    token_categories: MiddlewareDBTokenCategory
    urls: MiddlewareDBURL
    url_categories: MiddlewareDBURLCategory
    tasks: MiddlewareDBTask

    @abstractmethod
    def close(self):
        """Method to trigger any cleanup actions."""
        pass

    @abstractmethod
    def migrate(self):
        """Method to migrate the database schema."""
        pass
