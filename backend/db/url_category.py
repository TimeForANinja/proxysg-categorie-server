from abc import ABC, abstractmethod
from typing import List

class UrlCategoryDBInterface(ABC):
    @abstractmethod
    def create_table(self) -> None:
        """
        Create the 'url_category' table if it doesn't exist.
        """
        pass

    def get_url_categories_by_url(self, url_id: int) -> List[int]:
        """
        Get all categories of a URL

        :param url_id: The ID of the URL
        """
        pass

    def add_url_category(self, url_id: int, category_id: int) -> None:
        """
        Add a new mapping of URL and Category

        :param url_id: The ID of the URL
        :param category_id: The ID of the Category
        """
        pass

    def delete_url_category(self, url_id: int, category_id: int) -> None:
        """
        Delete a mapping of URL and Category.

        :param url_id: The ID of the URL
        :param category_id: The ID of the Category
        """
        pass
