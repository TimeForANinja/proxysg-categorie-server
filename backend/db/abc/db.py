from abc import ABC, abstractmethod
from typing import Dict, Any, List


class DBInterface(ABC):
    @abstractmethod
    def close(self):
        """
        Method to trigger any cleanup actions.
        This might cause the DBInterface to become unusable.
        """
        pass

    @abstractmethod
    def has_key(self, key: str) -> bool:
        pass

    @abstractmethod
    def fetch_kv(self, hash: str) -> str|bytes:
        pass

    @abstractmethod
    def insert_kv(self, key: str, value: str|bytes):
        pass

    @abstractmethod
    def fetch_obj(self, hash: str) -> Dict[Any, Any]:
        pass

    @abstractmethod
    def insert_obj(self, entry: Dict[Any, Any]) -> str:
        pass

    @abstractmethod
    def fetch_id_list(self, hash: str) -> List[str]:
        pass

    @abstractmethod
    def insert_id_list(self, entries: List[str]) -> str:
        pass
