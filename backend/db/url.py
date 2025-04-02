from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length

from db.util.validators import simpleURLValidator, simpleStringValidator


@dataclass(kw_only=True)
class MutableURL:
    hostname: str = field(metadata={
        "required": True,
        "validate": [
            Length(min=4),
            simpleURLValidator,
        ],
        "description": "FQDN of the URL",
    })
    description: str = field(metadata={
        "required": True,
        "validate": [
            Length(max=255),
            simpleStringValidator,
        ],
        "description": "Description of the token"
    })

@dataclass(kw_only=True)
class URL(MutableURL):
    """
    Helper class to represent a URL.
    """
    id: str = field(metadata={
        "required": True,
        "description": "ID of the URL",
    })
    hostname: str = field(metadata={
        "required": True,
        "validate": [
            Length(min=4),
            simpleURLValidator,
        ],
        "description": "FQDN of the URL",
    })
    description: str = field(metadata={
        "required": True,
        "validate": [
            Length(max=255),
            simpleStringValidator,
        ],
        "description": "Description of the token"
    })
    is_deleted: int = field(
        default=0,
        metadata={
            "description": "Whether the url is deleted or not",
        }
    )
    categories: List[str] = field(
        default_factory=list,
        metadata={
            "description": "List of category IDs associated with the URL",
        }
    )


class URLDBInterface(ABC):
    @abstractmethod
    def create_table(self) -> None:
        """
        Create the 'url' table if it doesn't exist.
        """
        pass

    @abstractmethod
    def add_url(self, url: MutableURL) -> URL:
        """
        Add a new url with the given hostname.

        :param url: The (partial) url to add.
        :return: The newly created url.
        """
        pass

    @abstractmethod
    def get_url(self, url_id: str) -> Optional[URL]:
        """
        Retrieve the details of a specific url by its ID.

        :param url_id: The ID of the url to retrieve.
        :return: A URL
                 or None if the url doesn't exist or is marked as deleted.
        """
        pass

    @abstractmethod
    def update_url(
            self,
            url_id: str,
            url: MutableURL,
    ) -> URL:
        """
        Update the details of a specific url.

        :param url_id: The ID of the url to update.
        :param url: The (partial) url to update.
        """
        pass

    @abstractmethod
    def delete_url(self, url_id: str) -> None:
        """
        Soft delete an url by setting its `is_deleted` flag to 1.

        :param url_id: The ID of the url to delete.
        """
        pass

    @abstractmethod
    def get_all_urls(self) -> List[URL]:
        """
        Retrieve all active URLs that are not marked as deleted.

        :return: A list of URLs
        """
        pass
