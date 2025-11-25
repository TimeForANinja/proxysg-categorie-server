from abc import ABC, abstractmethod
from typing import Optional, List

from auth.auth_user import AuthUser
from db.dbmodel.url import MutableURL, URL


class MiddlewareDBURL(ABC):
    @abstractmethod
    def add_url(self, auth: AuthUser, mut_url: MutableURL) -> URL:
        """
        Add a new url with the given hostname.

        :param auth: The authenticated user.
        :param mut_url: The (partial) url to add.
        :return: The newly created url.
        """
        pass

    def add_urls(self, auth: AuthUser, mut_urls: List[MutableURL]) -> List[URL]:
        """
        Add a batch of urls with the given hostnames.

        :param auth: The authenticated user.
        :param mut_urls: The (partial) urls to add.
        :return: The newly created urls.
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
    def update_url(self, auth: AuthUser, url_id: str, mut_url: MutableURL) -> URL:
        """
        Update the details of a specific url.

        :param auth: The authenticated user.
        :param url_id: The ID of the url to update.
        :param mut_url: The (partial) url to update.
        """
        pass

    @abstractmethod
    def delete_url(self, auth: AuthUser, url_id: str):
        """
        Soft-delete a URL by setting its `is_deleted` flag to the current timestamp.

        :param auth: The authenticated user.
        :param url_id: The ID of the url to delete.
        """
        pass

    @abstractmethod
    def get_all_urls(self, bypass_cache: bool = False) -> List[URL]:
        """
        Retrieve all active URLs that are not marked as deleted.

        :param bypass_cache: If True, bypass the cache and retrieve the URLs from the database.
        :return: A list of URLs
        """
        pass

    @abstractmethod
    def set_bc_cats(self, url_id: str, bc_cats: List[str]):
        """
        Update the BlueCoat Categories associated with a URL.

        :param url_id: The ID of the url to update.
        :param bc_cats: The list of BlueCoat Categories to associate with the URL.
        """
        pass
