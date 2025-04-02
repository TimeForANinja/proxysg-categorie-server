from abc import ABC, abstractmethod
from typing import List

class TokenCategoryDBInterface(ABC):
    @abstractmethod
    def create_table(self) -> None:
        """
        Create the 'token_category' table if it doesn't exist.
        """
        pass

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        """
        Get all categories of a Token

        :param token_id: The ID of the Token
        """
        pass

    def add_token_category(self, token_id: str, category_id: str) -> None:
        """
        Add a new mapping of Token and Category

        :param token_id: The ID of the Token
        :param category_id: The ID of the Category
        """
        pass

    def delete_token_category(self, token_id: str, category_id: str) -> None:
        """
        Delete a mapping of Token and Category.

        :param token_id: The ID of the Token
        :param category_id: The ID of the Category
        """
        pass
