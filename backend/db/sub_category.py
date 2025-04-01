from abc import ABC, abstractmethod
from typing import List


class SubCategoryDBInterface(ABC):
    @abstractmethod
    def create_table(self) -> None:
        """
        Create the 'sub_category' table if it doesn't exist.
        """
        pass

    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        """
        Get all sub-categories of a category

        :param category_id: The ID of the Category
        """
        pass

    def add_sub_category(self, category_id: str, sub_category_id: str) -> None:
        """
        Add a new sub-category

        :param category_id: The ID of the parent-category
        :param sub_category_id: The ID of the sub-category
        """
        pass

    def delete_sub_category(self, category_id: str, sub_category_id: str) -> None:
        """
        Delete a mapping of a sub-category.

        :param category_id: The ID of the parent-category
        :param sub_category_id: The ID of the sub-category
        """
        pass
