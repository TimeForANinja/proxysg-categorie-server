from abc import ABC, abstractmethod
from typing import List, Dict

from auth.auth_user import AuthUser


class MiddlewareDBURLCategory(ABC):
    @abstractmethod
    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        """
        Get all categories of a URL

        :param url_id: The ID of the URL
        """
        pass

    @abstractmethod
    def add_url_category(self, auth: AuthUser, url_id: str, cat_id: str):
        """
        Add a new mapping of URL and Category

        :param auth: The authenticated user
        :param url_id: The ID of the URL
        :param cat_id: The ID of the Category
        """
        pass

    @abstractmethod
    def add_url_categories(self, auth: AuthUser, mappings: Dict[str, List[str]]):
        """
        Add a batch of new URL to Category mappings

        :param auth: The authenticated user
        :param mappings: A list of Tuples, where each Tuple contains the URL ID and the Category ID
        """
        pass

    @abstractmethod
    def delete_url_category(self, auth: AuthUser, url_id: str, cat_id: str):
        """
        Delete a mapping of URL and Category.

        :param auth: The authenticated user
        :param url_id: The ID of the URL
        :param cat_id: The ID of the Category
        """
        pass

    @abstractmethod
    def set_url_categories(self, auth: AuthUser, url_id: str, cat_ids: List[str]):
        """
        Set Categories of a URL.

        :param auth: The authenticated user
        :param url_id: The ID of the URL
        :param cat_ids: The IDs of the categories
        """
        pass
