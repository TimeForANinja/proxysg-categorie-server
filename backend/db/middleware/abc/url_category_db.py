from abc import ABC, abstractmethod
from typing import List

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
    def add_url_category(self, auth: AuthUser, url_id: str, cat_id: str) -> None:
        """
        Add a new mapping of URL and Category

        :param auth: The authenticated user
        :param url_id: The ID of the URL
        :param cat_id: The ID of the Category
        """
        pass

    @abstractmethod
    def delete_url_category(self, auth: AuthUser, url_id: str, cat_id: str) -> None:
        """
        Delete a mapping of URL and Category.

        :param auth: The authenticated user
        :param url_id: The ID of the URL
        :param cat_id: The ID of the Category
        """
        pass

    @abstractmethod
    def set_url_categories(self, auth: AuthUser, url_id: str, cat_ids: List[str]) -> None:
        """
        Set Categories of a URL.

        :param auth: The authenticated user
        :param url_id: The ID of the URL
        :param cat_ids: The IDs of the categories
        """
        pass
