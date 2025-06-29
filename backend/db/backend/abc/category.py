from abc import ABC, abstractmethod
from typing import Optional, List

from db.dbmodel.category import MutableCategory, Category


class CategoryDBInterface(ABC):
    @abstractmethod
    def add_category(self, category: MutableCategory, category_id: str) -> Category:
        """
        Add a new category with the given name, color, and an optional description.

        :param category: The (partial) category to add.
        :param category_id: The ID of the category to add. This is used to identify the category in the database.
        :return: The newly created category.
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
    def update_category(
            self,
            cat_id: str,
            category: MutableCategory,
    ) -> Category:
        """
        Update the details of a specific category.

        :param cat_id: The ID of the category to update.
        :param category: The (partial) category to update.
        """
        pass

    @abstractmethod
    def delete_category(self, category_id: str) -> None:
        """
        Soft-delete a category by setting its `is_deleted` flag to the current timestamp.

        :param category_id: The ID of the category to delete.
        """
        pass

    @abstractmethod
    def get_all_categories(self) -> List[Category]:
        """
        Retrieve all active categories that are not marked as deleted.

        :return: A list of categories
        """
        pass
