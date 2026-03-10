from abc import ABC, abstractmethod

from db.middleware.abc.category_db import MiddlewareDBCategory
from db.middleware.abc.url_db import MiddlewareDBURL


class MiddlewareDB(ABC):
    categories: MiddlewareDBCategory
    urls: MiddlewareDBURL

    @abstractmethod
    def close(self):
        """Method to trigger any cleanup actions."""
        pass

    @abstractmethod
    def migrate(self):
        """Method to migrate the database schema."""
        pass
