from abc import ABC, abstractmethod
from typing import Optional, List

from db.backend.abc.util.types import MyTransactionType
from db.dbmodel.category import MutableCategory, Category


class CategoryDBInterface(ABC):
    @abstractmethod
    def add_category(self, category: MutableCategory, session: Optional[MyTransactionType] = None) -> str:
        """
        Add a new category with the given name, color, and an optional description.

        :param category: The (partial) category to add.
        :param session: Optional database session to use
        :return: The ID of the newly created category.
        """
        pass

    @abstractmethod
    def get_category(self, category_id: str, session: Optional[MyTransactionType] = None) -> Optional[Category]:
        """
        Retrieve the details of a specific category by its ID.

        :param category_id: The ID of the category to retrieve.
        :param session: Optional database session to use
        :return: A Category
                 or None if the category doesn't exist or is marked as deleted.
        """
        pass

    @abstractmethod
    def update_category(
        self,
        cat_id: str,
        category: MutableCategory,
        session: Optional[MyTransactionType] = None,
    ) -> Category:
        """
        Update the details of a specific category.

        :param cat_id: The ID of the category to update.
        :param category: The (partial) category to update.
        :param session: Optional database session to use
        """
        pass


    @abstractmethod
    def get_all_categories(self, session: Optional[MyTransactionType] = None) -> List[Category]:
        """
        Retrieve all active categories that are not marked as deleted.

        :param session: Optional database session to use
        :return: A list of categories
        """
        pass
