from abc import ABC, abstractmethod
from typing import List, Tuple


class UrlCategoryDBInterface(ABC):
    @abstractmethod
    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        """
        Get all categories of a URL

        :param url_id: The ID of the URL
        """
        pass

    @abstractmethod
    def add_url_category(self, url_id: str, category_id: str) -> None:
        """
        Add a new mapping of URL and Category

        :param url_id: The ID of the URL
        :param category_id: The ID of the Category
        """
        pass

    @abstractmethod
    def bulk_add_url_category(self, sets: List[Tuple[str, str]]) -> None:
        """
        Bulk add URL and Category mapping.

        :param sets: A list of tuples (url_id, category_id)
        """
        pass

    @abstractmethod
    def delete_url_category(self, url_id: str, category_id: str) -> None:
        """
        Delete a mapping of URL and Category.

        :param url_id: The ID of the URL
        :param category_id: The ID of the Category
        """
        pass
