from abc import ABC, abstractmethod
from typing import List

from auth.auth_user import AuthUser


class MiddlewareDBTokenCategory(ABC):
    @abstractmethod
    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        """
        Get all categories of a Token

        :param token_id: The ID of the Token
        """
        pass

    @abstractmethod
    def add_token_category(self, auth: AuthUser, token_id: str, cat_id: str):
        """
        Add a new mapping of Token and Category

        :param auth: The authenticated user
        :param token_id: The ID of the Token
        :param cat_id: The ID of the Category
        """
        pass

    @abstractmethod
    def delete_token_category(self, auth: AuthUser, token_id: str, cat_id: str):
        """
        Delete a mapping of Token and Category.

        :param auth: The authenticated user
        :param token_id: The ID of the Token
        :param cat_id: The ID of the Category
        """
        pass

    @abstractmethod
    def set_token_categories(self, auth: AuthUser, token_id: str, cat_ids: List[str]):
        """
        Set the categories of a token.

        :param auth: The authenticated user
        :param token_id: The ID of the Token
        :param cat_ids: The IDs of the categories
        """
        pass
