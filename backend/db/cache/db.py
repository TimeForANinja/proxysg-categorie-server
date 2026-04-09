from typing import Any, Dict, List

from cachetools import LFUCache

from db.abc.db import DBInterface


DEFAULT_CACHE_CAPACITY = 1_000_000


class CacheDB(DBInterface):
    def __init__(self, parent: DBInterface, capacity: int = DEFAULT_CACHE_CAPACITY):
        super().__init__()
        self.capacity = capacity

        self.kv_cache = LFUCache(maxsize=capacity)
        self.obj_cache = LFUCache(maxsize=capacity)
        self.id_list_cache = LFUCache(maxsize=capacity)

        self.parent = parent


    def close(self):
        # clear cache
        self.kv_cache = LFUCache(maxsize=self.capacity)
        self.obj_cache = LFUCache(maxsize=self.capacity)
        self.id_list_cache = LFUCache(maxsize=self.capacity)
        # then forward call to parent
        self.parent.close()


    def has_key(self, key: str) -> bool:
        return self.parent.has_key(key)


    def fetch_kv(self, key: str) -> str|bytes:
        if key in self.kv_cache:
            return self.kv_cache[key]
        return self.parent.fetch_kv(key)

    def fetch_obj(self, obj_hash: str) -> Dict[Any, Any]:
        if obj_hash in self.obj_cache:
            return self.obj_cache[obj_hash]
        return self.parent.fetch_obj(obj_hash)

    def fetch_id_list(self, obj_hash: str) -> List[str]:
        if obj_hash in self.id_list_cache:
            return self.id_list_cache[obj_hash]
        return self.parent.fetch_id_list(obj_hash)


    def insert_kv(self, key: str, value: str|bytes):
        # pass all writes to parent
        return self.parent.insert_kv(key, value)

    def insert_obj(self, entry: Dict[Any, Any]) -> str:
        # pass all writes to parent
        return self.parent.insert_obj(entry)

    def insert_id_list(self, entries: List[str]) -> str:
        # pass all writes to parent
        return self.parent.insert_id_list(entries)
