from typing import Any, Dict, List, Optional, TypeVar, Protocol
# use cachebox instead of cachetools since it's thread-safe
from cachebox import LFUCache, BaseCacheImpl

from db.abc.db import DBInterface
from util.log import log_debug

T = TypeVar("T")


class FetchUpstreamCallback(Protocol):
    # custom object so we can support kwargs
    def __call__(self, obj_hashes: List[str], **kwargs: Any) -> List[T]:
        ...


DEFAULT_CACHE_CAPACITY = 1_000_000


class CacheDB(DBInterface):
    """
    LRU/LFU Caching Middleware for database backends.
    Wraps another DBInterface implementation and caches read operations.
    Write operations are always passed through to the parent backend.
    """
    def __init__(self, parent: DBInterface, capacity: int = DEFAULT_CACHE_CAPACITY):
        """
        Initialize the cache wrapper.

        :param parent: The underlying DB backend to wrap.
        :param capacity: Maximum number of entries per cache category (KV, Obj, ID List).
        """
        super().__init__()
        self.capacity = capacity

        self.obj_cache = LFUCache(maxsize=capacity)
        self.id_list_cache = LFUCache(maxsize=capacity)

        self.parent = parent


    def close(self):
        """
        Clear all local caches and forward the close command to the parent backend.
        """
        log_debug("DB", "Closing CacheDB")
        # clear cache by reinitializing
        self.obj_cache = LFUCache(maxsize=self.capacity)
        self.id_list_cache = LFUCache(maxsize=self.capacity)
        # then forward call to parent
        self.parent.close()

    def get_metrics(self) -> Dict[str, Any]:
        return {
            **self.parent.get_metrics(),
            "cache-capacity": self.capacity,
            "cache-size-obj": len(self.obj_cache),
            "cache-size-id-list": len(self.id_list_cache),
            "cache-size-obj-perc": f"{len(self.obj_cache) / self.capacity * 100:2.2f} %",
            "cache-size-id-list-perc": f"{len(self.id_list_cache) / self.capacity * 100:2.2f} %",
        }


    @staticmethod
    def _generic_cached_fetch(
            keys: List[str],
            cache: BaseCacheImpl[str, T],
            fetch_upstream: FetchUpstreamCallback,
            **kwargs
    ) -> List[T]:
        """
        Generic method to fetch data from the cache, or if not found, fetch from the upstream DB.

        :param keys: The keys to fetch from the cache or upstream.
        :param cache: The cache to check for existing values.
        :param fetch_upstream: The function to fetch (missing) values from the upstream DB.
        :param kwargs: Additional arguments (to pass to the fetch_upstream function).
        :return: List of fetched values corresponding to the input keys.
        """
        results: List[Optional[T]] = [None] * len(keys)
        missing_indices: List[int] = []

        if kwargs.get("bypass_cache", False):
            # cache disabled -> fetch all from upstream
            missing_indices = list(range(len(keys)))
        else:
            # check cache before forwarding to backend
            for i, key in enumerate(keys):
                if key in cache:
                    cached = cache[key]
                    if hasattr(cached, "copy"):
                        # create a copy before returning, to avoid modifying cached data
                        # (e.g., fetching an array and pushing a new element to it)
                        results[i] = cached.copy()
                    else:
                        results[i] = cached
                else:
                    missing_indices.append(i)

        if missing_indices:
            # fetch missing values from upstream
            fetched_values = fetch_upstream([
                keys[i] for i in missing_indices
            ], **kwargs)
            for i, val in zip(missing_indices, fetched_values):
                results[i] = val
                # add to cache for future use
                cache[keys[i]] = val

        return results


    def batch_fetch_obj(self, obj_hashes: List[str], **kwargs) -> List[Dict[str, Any]]:
        return CacheDB._generic_cached_fetch(obj_hashes, self.obj_cache, self.parent.batch_fetch_obj, **kwargs)

    def batch_fetch_id_list(self, obj_hashes: List[str], **kwargs) -> List[List[str]]:
        return CacheDB._generic_cached_fetch(obj_hashes, self.id_list_cache, self.parent.batch_fetch_id_list)


    def batch_set_obj(self, key: List[str], val: List[Dict[str, Any]]) -> None:
        self.parent.batch_set_obj(key, val)
        # update cache
        for key, val in zip(key, val):
            self.obj_cache[key] = val

    def batch_insert_obj(self, entries: List[Dict[str, Any]]) -> List[str]:
        keys = self.parent.batch_insert_obj(entries)
        # update cache
        for key, val in zip(keys, entries):
            self.obj_cache[key] = val
        return keys

    def batch_insert_id_list(self, entries_list: List[List[str]]) -> List[str]:
        keys = self.parent.batch_insert_id_list(entries_list)
        # update cache
        for key, val in zip(keys, entries_list):
            self.id_list_cache[key] = val
        return keys
