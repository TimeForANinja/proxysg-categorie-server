from abc import ABC, abstractmethod
from typing import Optional, List, ClassVar, Final


class TagsDBInterface(ABC):
    MASTER: ClassVar[Final[str]] = "Master"
    STAGED: ClassVar[Final[str]] = "Staged"

    @abstractmethod
    def set_tag_hash(self, label: str, hash: str):
        """
        Set the hash for a specific tag label.

        :param label: The label of the tag.
        :param hash: The hash to associate with the label.
        """
        pass

    @abstractmethod
    def get_tag_hash(self, label: str) -> Optional[str]:
        """
        Retrieve the hash associated with a tag label.

        :param label: The label of the tag.
        :return: The hash or None if not found.
        """
        pass


class BaseSetDBInterface(ABC):
    @abstractmethod
    def insert(self, uuid: str, entries: List[str]):
        """
        Map a UUID to a set of entries.

        :param uuid: The UUID for the set.
        :param entries: The list of UUIDs.
        """
        pass

    def _insert(self, uuid: str, type: str, entries: List[str]):
        pass

    @abstractmethod
    def get(self, uuid: str) -> Optional[List[str]]:
        """
        Retrieve the entries for a given UUID and type.

        :param uuid: The UUID for the set.
        :return: The list of UUIDs or None if not found.
        """
        pass

    def _get(self, uuid: str, type: str) -> Optional[List[str]]:
        pass


class CategorySetDBInterface(BaseSetDBInterface):
    def insert(self, uuid: str, entries: List[str]):
        super()._insert(uuid, "category", entries)

    def get(self, uuid: str) -> Optional[List[str]]:
        return super()._get(uuid, "category")


class URLSetDBInterface(BaseSetDBInterface):
    def insert(self, uuid: str, entries: List[str]):
        super()._insert(uuid, "url", entries)

    def get(self, uuid: str) -> Optional[List[str]]:
        return super()._get(uuid, "url")
