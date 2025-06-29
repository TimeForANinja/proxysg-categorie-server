from abc import ABC, abstractmethod
from typing import List


class TokenCategoryDBInterface(ABC):
    @abstractmethod
    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        """
        Get all categories of a Token

        :param token_id: The ID of the Token
        """
        pass

    @abstractmethod
    def add_token_category(self, token_id: str, category_id: str) -> None:
        """
        Add a new mapping of Token and Category

        :param token_id: The ID of the Token
        :param category_id: The ID of the Category
        """
        pass

    @abstractmethod
    def delete_token_category(self, token_id: str, category_id: str) -> None:
        """
        Delete a mapping of Token and Category.

        :param token_id: The ID of the Token
        :param category_id: The ID of the Category
        """
        pass
