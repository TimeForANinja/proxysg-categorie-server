from abc import ABC, abstractmethod
from typing import List, Optional

from db.backend.abc.util.types import MyTransactionType


class TokenCategoryDBInterface(ABC):
    @abstractmethod
    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        """
        Get all categories of a Token

        :param token_id: The ID of the Token
        """
        pass

    @abstractmethod
    def add_token_category(
        self,
        token_id: str,
        category_id: str,
        session: Optional[MyTransactionType] = None,
    ):
        """
        Add a new mapping of Token and Category

        :param token_id: The ID of the Token
        :param category_id: The ID of the Category
        :param session: Optional database session to use
        """
        pass

    @abstractmethod
    def delete_token_category(
        self,
        token_id: str,
        category_id: str,
        del_timestamp: int,
        session: Optional[MyTransactionType] = None,
    ):
        """
        Delete a mapping of Token and Category.

        :param token_id: The ID of the Token
        :param category_id: The ID of the Category
        :param del_timestamp: The timestamp to set as deletion timestamp
        :param session: Optional database session to use
        """
        pass
