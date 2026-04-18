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
    def has_key(self, key: str) -> bool:
        """
        Check if a given key exists in the database.

        :param key: The unique identifier (e.g., Hash) to check.
        :return: True if the key exists, False otherwise.
        """
        pass

    @abstractmethod
    def fetch_kv(self, key: str) -> str | bytes:
        """
        Retrieve a raw value (string or bytes) associated with a key.

        :param key: The unique identifier.
        :return: The stored value.
        :raises KeyError: If the key is not found.
        """
        pass

    @abstractmethod
    def insert_kv(self, key: str, value: str | bytes):
        """
        Insert or update a raw value associated with a key.

        :param key: The unique identifier.
        :param value: The value to store.
        """
        pass

    @abstractmethod
    def fetch_obj(self, obj_hash: str) -> Dict[Any, Any]:
        """
        Retrieve a dictionary object by its hash.

        :param obj_hash: The SHA256 hash of the object.
        :return: The decoded dictionary.
        :raises KeyError: If the hash is not found.
        """
        pass

    @abstractmethod
    def insert_obj(self, entry: Dict[Any, Any]) -> str:
        """
        Insert a dictionary object and return its generated hash.

        :param entry: The dictionary to store.
        :return: The SHA256 hash of the stored object.
        """
        pass

    @abstractmethod
    def fetch_id_list(self, obj_hash: str) -> List[str]:
        """
        Retrieve a list of strings (typically IDs) by its hash.
        Handles both small (direct) and large (sharded) lists transparently.

        :param obj_hash: The SHA256 hash of the list.
        :return: The list of strings.
        :raises KeyError: If the hash is not found.
        """
        pass

    @abstractmethod
    def insert_id_list(self, entries: List[str]) -> str:
        """
        Insert a list of strings and return its generated hash.
        May shard large lists into multiple entries for performance and storage limits.

        :param entries: The list of strings to store.
        :return: The SHA256 hash of the list (or its root entry).
        """
        pass
