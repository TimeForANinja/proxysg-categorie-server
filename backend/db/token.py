from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length

from db.util.validators import simpleStringValidator


@dataclass(kw_only=True)
class MutableToken:
    description: str = field(metadata={
        'required': True,
        'validate': [
            Length(max=255),
            simpleStringValidator,
        ],
        'description': 'Description of the token'
    })


@dataclass(kw_only=True)
class Token(MutableToken):
    """
    Helper class to represent a token.
    """
    id: str = field(metadata={
        'required': True,
        'description': 'ID of the token',
    })
    token: str = field(metadata={
        'required': True,
        # uuid v4 is always 36 characters
        'validate': Length(min=36, max=36),
        'description': 'Token for use with the API',
    })
    description: str = field(metadata={
        'required': True,
        'validate': [
            Length(max=255),
            simpleStringValidator,
        ],
        'description': 'Description of the token'
    })
    last_use: int = field(
        default=0,
        metadata={
            'description': 'Timestamp when the token was last used',
        }
    )
    is_deleted: int = field(
        default=0,
        metadata={
            'description': 'Whether the token is deleted or not',
        }
    )
    categories: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of category IDs associated with the URL',
        }
    )


class TokenDBInterface(ABC):

    @abstractmethod
    def add_token(self, uuid: str, mut_tok: MutableToken) -> Token:
        """
        Add a new token with the given name, and an optional description.

        :param uuid: The UUID (token) of the token.
        :param mut_tok: The (partial) token to add.
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
