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
    ) -> str:
        """
        Add a new subcategory

        :param category_id: The ID of the parent-category
        :param sub_category_id: The ID of the subcategory
        :param session: Optional database session to use
        :return: The ID of the newly created entry.
        """
        pass

