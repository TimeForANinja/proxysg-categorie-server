from abc import ABC, abstractmethod
from typing import Optional, List

from auth.auth_user import AuthUser
from db.dbmodel.category import MutableCategory, Category


class MiddlewareDBCategory(ABC):
    @abstractmethod
    def add_category(self, auth: AuthUser, category: MutableCategory) -> Category:
        """
        Add a new category with the given name, color and an optional description.

        :param auth: The authenticated user.
        :param category: The (partial) category to add.
        :return: The newly created category.
        """
        pass

    def add_categories(self, auth: AuthUser, categories: List[MutableCategory]) -> List[Category]:
        """
        Add a batch of categories with the given name, color and an optional description.

        :param auth: The authenticated user.
        :param categories: The (partial) categories to add.
        :return: The newly created categories.
        """
        pass

    @abstractmethod
    def get_category(self, category_id: str) -> Optional[Category]:
        """
        Retrieve the details of a specific category by its ID.

        :param category_id: The ID of the category to retrieve.
        :return: A Category
                 or None if the category doesn't exist or is marked as deleted.
        """
        pass

    @abstractmethod
    def update_category(self, auth: AuthUser, cat_id: str, category: MutableCategory) -> Category:
        """
        Update the details of a specific category.

        :param auth: The authenticated user.
        :param cat_id: The ID of the category to update.
        :param category: The (partial) category to update.
        """
        pass

    @abstractmethod
    def delete_category(self, auth: AuthUser, cat_id: str) -> None:
        """
        Soft-delete a category by setting its `is_deleted` flag to the current timestamp.

        :param auth: The authenticated user.
        :param cat_id: The ID of the category to delete.
        """
        pass

    @abstractmethod
    def get_all_categories(self) -> List[Category]:
        """
        Retrieve all active categories that are not marked as deleted.

        :return: A list of categories
        """
        pass
