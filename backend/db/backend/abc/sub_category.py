from abc import ABC, abstractmethod
from typing import List, Optional

from db.backend.abc.util.types import MyTransactionType


class SubCategoryDBInterface(ABC):
    @abstractmethod
    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        """
        Get all subcategories of a category

        :param category_id: The ID of the Category
        """
        pass

    @abstractmethod
    def add_sub_category(
        self,
        category_id: str,
        sub_category_id: str,
        session: Optional[MyTransactionType] = None,
    ):
        """
        Add a new subcategory

        :param category_id: The ID of the parent-category
        :param sub_category_id: The ID of the subcategory
        :param session: Optional database session to use
        """
        pass

    @abstractmethod
    def delete_sub_category(
        self,
        category_id: str,
        sub_category_id: str,
        del_timestamp: int,
        session: Optional[MyTransactionType] = None,
    ):
        """
        Delete a mapping of a subcategory.

        :param category_id: The ID of the parent-category
        :param sub_category_id: The ID of the subcategory
        :param del_timestamp: The timestamp to set as deletion timestamp
        :param session: Optional database session to use
        """
        pass
