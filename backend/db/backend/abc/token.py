from abc import ABC, abstractmethod
from typing import Optional, List

from db.dbmodel.token import MutableToken, Token


class TokenDBInterface(ABC):
    @abstractmethod
    def add_token(self, uuid: str, mut_tok: MutableToken, token_id: str) -> Token:
        """
        Add a new token with the given name, and an optional description.

        :param uuid: The UUID (token) of the token.
        :param mut_tok: The (partial) token to add.
        :param token_id: The ID of the token to add. This is used to identify the token in the database.
        :return: The newly created token.
        """
        pass

    @abstractmethod
    def get_token(self, token_id: str) -> Optional[Token]:
        """
        Retrieve the details of a specific token by its ID.

        :param token_id: The ID of the token to retrieve.
        :return: A Token
                 or None if the token doesn't exist or is marked as deleted.
        """
        pass

    @abstractmethod
    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        """
        Fetch a Token based on the token.uuid string.

        :param token_uuid: The token.uuid string to search for.
        :return: A Token object or None if not found.
        """
        pass

    @abstractmethod
    def update_token(
            self,
            token_id: str,
            token: MutableToken,
    ) -> Token:
        """
        Update the details of a specific token.

        :param token_id: The ID of the token to update.
        :param token: The (partial) token to update.
        """
        pass

    @abstractmethod
    def update_usage(self, token_id: str) -> None:
        """
        Update the usage counter for a specified token identified by its ID.

        :param token_id: The ID of the token to update.
        """
        pass

    @abstractmethod
    def roll_token(
            self,
            token_id: str,
            uuid: str,
    ) -> Token:
        """
        Re-Roll the Token of a specific token.

        :param token_id: The ID of the token to update.
        :param uuid: The new token string to store.
        :return: The newly created token.
        """
        pass

    @abstractmethod
    def delete_token(self, token_id: str) -> None:
        """
        Soft-delete a token by setting its `is_deleted` flag to the current timestamp.

        :param token_id: The ID of the token to delete.
        """
        pass

    @abstractmethod
    def get_all_tokens(self) -> List[Token]:
        """
        Retrieve all active tokens that are not marked as deleted.

        :return: A list of tokens
        """
        pass
