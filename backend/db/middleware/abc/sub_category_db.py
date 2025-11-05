from abc import ABC, abstractmethod
from typing import List

from auth.auth_user import AuthUser


class MiddlewareDBSubCategory(ABC):
    @abstractmethod
    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        """
        Get all subcategories of a category

        :param category_id: The ID of the Category
        """
        pass

    @abstractmethod
    def add_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str):
        """
        Add a new subcategory

        :param auth: The authenticated user
        :param cat_id: The ID of the parent-category
        :param sub_cat_id: The ID of the subcategory
        """
        pass

    @abstractmethod
    def delete_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str):
        """
        Delete a mapping of a subcategory.

        :param auth: The authenticated user
        :param cat_id: The ID of the parent-category
        :param sub_cat_id: The ID of the subcategory
        """
        pass

    @abstractmethod
    def set_sub_categories(self, auth: AuthUser, cat_id: str, cat_ids: List[str]):
        """
        Set the subcategories of a category.

        :param auth: The authenticated user
        :param cat_id: The ID of the category
        :param cat_ids: The IDs of the subcategories
        """
        pass
