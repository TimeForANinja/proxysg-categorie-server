from abc import ABC, abstractmethod
from typing import Optional, List

from db.dbmodel.url import MutableURL, URL


class URLDBInterface(ABC):
    @abstractmethod
    def add_url(self, url: MutableURL, url_id: str) -> URL:
        """
        Add a new url with the given hostname.

        :param url: The (partial) url to add.
        :param url_id: The ID of the url to add. This is used to identify the url in the database.
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
