from abc import ABC, abstractmethod
from typing import List, Optional

from db.backend.abc.util.types import MyTransactionType


class UrlCategoryDBInterface(ABC):
    @abstractmethod
    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        """
        Get all categories of a URL

        :param url_id: The ID of the URL
        """
        pass

    @abstractmethod
    def add_url_category(
        self,
        url_id: str,
        category_id: str,
        session: Optional[MyTransactionType] = None,
    ):
        """
        Add a new mapping of URL and Category

        :param url_id: The ID of the URL
        :param category_id: The ID of the Category
        :param session: Optional database session to use
        """
        pass

    @abstractmethod
    def delete_url_category(
        self,
        url_id: str,
        category_id: str,
        del_timestamp: int,
        session: Optional[MyTransactionType] = None,
    ):
        """
        Delete a mapping of URL and Category.

        :param url_id: The ID of the URL
        :param category_id: The ID of the Category
        :param del_timestamp: The timestamp to set as deletion timestamp
        :param session: Optional database session to use
        """
        pass
