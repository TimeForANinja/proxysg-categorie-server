from abc import ABC, abstractmethod
from typing import Dict, Any, List


class DBInterface(ABC):
    """
    Abstract Base Class for database interactions.
    Defines the contract for all persistent and middleware database backends.
    """

    @abstractmethod
    def close(self):
        """
        Close the database connection and perform any necessary cleanup.
        After calling this, the instance may become unusable.
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retrieve metrics from the database.

        :return: A dictionary containing database metrics.
        """
        pass


    @abstractmethod
    def batch_fetch_kv(self, keys: List[str]) -> List[str | bytes]:
        """
        Retrieve a list of raw values associated with a list of keys.

        :param keys: The unique identifiers.
        :return: A list of stored values.
        :raises KeyError: If any key is not found.
        """
        pass

    @abstractmethod
    def batch_insert_kv(self, keys: List[str], values: List[str | bytes]) -> None:
        """
        Insert or update a list of raw values associated with a list of keys.

        :param keys: The unique identifiers.
        :param values: The values to store.
        """
        pass


    @abstractmethod
    def batch_fetch_obj(self, obj_hashes: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve a list of dictionary objects by their hashes.

        :param obj_hashes: The SHA256 hashes of the objects.
        :return: A list of decoded dictionaries.
        :raises KeyError: If any hash is not found.
        """
        pass

    @abstractmethod
    def batch_insert_obj(self, entries: List[Dict[str, Any]]) -> List[str]:
        """
        Insert a list of dictionary objects and return their generated hashes.

        :param entries: The list of dictionaries to store.
        :return: A list of SHA256 hashes of the stored objects.
        """
        pass


    @abstractmethod
    def batch_fetch_id_list(self, obj_hashes: List[str]) -> List[List[str]]:
        """
        Retrieve a list of ID lists by their hashes.

        :param obj_hashes: The SHA256 hashes of the lists.
        :return: A list of lists of strings.
        :raises KeyError: If any hash is not found.
        """
        pass

    @abstractmethod
    def batch_insert_id_list(self, entries_list: List[List[str]]) -> List[str]:
        """
        Insert a list of ID lists and return their generated hashes.

        :param entries_list: A list of lists of strings to store.
        :return: A list of SHA256 hashes of the stored lists.
        """
        pass
