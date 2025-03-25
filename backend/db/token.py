from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length


@dataclass(kw_only=True)
class MutableToken:
    description: str = field(metadata={
        "required": True,
        "validate": Length(max=255),
        "description": "Description of the token"
    })

@dataclass(kw_only=True)
class Token(MutableToken):
    """
    Helper class to represent a token.
    """
    id: int = field(metadata={
        "required": True,
        "description": "ID of the token",
    })
    token: str = field(metadata={
        "required": True,
        # uuid v4 is always 36 characters
        "validate": Length(min=36, max=36),
        "description": "Token for use with the API",
    })
    description: str = field(metadata={
        "required": True,
        "validate": Length(max=255),
        "description": "Description of the token"
    })
    last_use: int = field(
        default=0,
        metadata={
            "description": "Timestamp when the token was last used",
        }
    )
    is_deleted: int = field(
        default=0,
        metadata={
            "description": "Whether the token is deleted or not",
        }
    )
    categories: List[int] = field(default_factory=list)


class TokenDBInterface(ABC):
    @abstractmethod
    def create_table(self) -> None:
        """
        Create the 'tokens' table if it doesn't exist.
        """
        pass

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
    def get_token(self, token_id: int) -> Optional[Token]:
        """
        Retrieve the details of a specific token by its ID.

        :param token_id: The ID of the token to retrieve.
        :return: A Token
                 or None if the token doesn't exist or is marked as deleted.
        """
        pass

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
            token_id: int,
            token: MutableToken,
    ) -> Token:
        """
        Update the details of a specific token.

        :param token_id: The ID of the token to update.
        :param token: The (partial) token to update.
        """
        pass

    @abstractmethod
    def update_usage(self, token_id: int) -> None:
        """
        Update the usage counter for a  specified token identified by its ID.

        :param token_id: The ID of the token to update.
        """
        pass

    @abstractmethod
    def roll_token(
            self,
            token_id: int,
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
    def delete_token(self, token_id: int) -> None:
        """
        Soft delete a token by setting its `is_deleted` flag to 1.

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
