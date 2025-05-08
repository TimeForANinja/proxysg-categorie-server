from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length

from db.util.validators import simpleURLValidator, simpleStringValidator


# Default Value set in the bc_cats array
# It indicates that a URL has never been queried against the BC Database
NO_BC_CATEGORY_YET = 'to be queried'
# Value returned by BC if the Category-Service is not working
FAILED_BC_CATEGORY_LOOKUP = 'unavailable'


@dataclass(kw_only=True)
class MutableURL:
    hostname: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=4),
            simpleURLValidator,
        ],
        'description': 'FQDN of the URL',
    })
    description: str = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the token'
        },
    )

@dataclass(kw_only=True)
class URL(MutableURL):
    """
    Helper class to represent a URL.
    """
    id: str = field(metadata={
        'required': True,
        'description': 'ID of the URL',
    })
    hostname: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=4),
            simpleURLValidator,
        ],
        'description': 'FQDN of the URL',
    })
    description: str = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the token'
        },
    )
    is_deleted: int = field(
        default=0,
        metadata={
            'description': 'Whether the url is deleted or not',
        }
    )
    categories: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of category IDs associated with the URL',
        }
    )
    bc_cats: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of BlueCoat Categories this URL is currently categorised as',
        }
    )


class URLDBInterface(ABC):
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
        Soft-delete a URL by setting its `is_deleted` flag to the current timestamp.

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

    @abstractmethod
    def set_bc_cats(self, url_id: str, bc_cats: List[str]) -> None:
        """
        Update the BlueCoat Categories associated with a URL.

        :param url_id: The ID of the url to update.
        :param bc_cats: The list of BlueCoat Categories to associate with the URL.
        """
        pass
