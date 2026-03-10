from abc import ABC, abstractmethod
from typing import Optional, List

from db.backend.abc.util.types import MyTransactionType
from db.dbmodel.url import MutableURL, URL


class URLDBInterface(ABC):
    @abstractmethod
    def add_url(self, url: MutableURL, session: Optional[MyTransactionType] = None) -> str:
        """
        Add a new url with the given hostname.

        :param url: The (partial) url to add.
        :param session: Optional database session to use
        :return: The ID of the newly created url.
        """
        pass

    @abstractmethod
    def get_url(self, url_id: str, session: Optional[MyTransactionType] = None) -> Optional[URL]:
        """
        Retrieve the details of a specific url by its ID.

        :param url_id: The ID of the url to retrieve.
        :param session: Optional database session to use
        :return: A URL
                 or None if the url doesn't exist or is marked as deleted.
        """
        pass

    @abstractmethod
    def update_url(self, url_id: str, url: MutableURL, session: Optional[MyTransactionType] = None) -> URL:
        """
        Update the details of a specific url.

        :param url_id: The ID of the url to update.
        :param url: The (partial) url to update.
        :param session: Optional database session to use
        """
        pass

    @abstractmethod
    def get_all_urls(self, session: Optional[MyTransactionType] = None) -> List[URL]:
        """
        Retrieve all active URLs that are not marked as deleted.

        :param session: Optional database session to use
        :return: A list of URLs
        """
        pass
