from collections import defaultdict
from typing import Dict, Any, List, Mapping
from pymongo import MongoClient

from db.abc.db import DBInterface
from db.abc.constants import KEY_LENGTH, MAX_COMPACT_LIST_SIZE, TYPE_ID_LIST_SMALL, TYPE_ID_LIST_LARGE
from db.dbm.util.simple_bson import encode_dict_str, encode_list_str
from db.dbm.util.hash import sha256_hash


class MongoDB(DBInterface):
    def __init__(self, host: str, port: int, database_name: str, collection_name: str = "data"):
        super().__init__()
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

        # Create an index on "_key" for fast lookups
        self.collection.create_index("_key", unique=True)

    def close(self):
        self.client.close()


    def has_key(self, key: str) -> bool:
        return self.collection.find_one({"_key": key}) is not None


    def fetch_kv(self, key: str) -> str|bytes:
        doc = self.collection.find_one({"_key": key})
        if doc is None:
            raise KeyError(key)
        return doc["value"]

    def insert_kv(self, key: str, value: str|bytes):
        self.collection.update_one(
            {"_key": key},
            {"$set": {"value": value}},
            upsert=True
        )


    def fetch_obj(self, obj_hash: str) -> Dict[Any, Any]:
        doc = self.collection.find_one({"_key": obj_hash})
        if doc is None:
            raise KeyError(obj_hash)
        # MongoDB already stores the data as a dict, so no typecast required

        # We need to remove the _id from the result if we ever fetched the whole doc.
        data = doc["data"]
        return data

    def insert_obj(self, entry: Dict[Any, Any]) -> str:
        # reuse the same hash function as DBM for constitency
        entry_hash = sha256_hash(encode_dict_str(entry))
        
        self.collection.update_one(
            {"_key": entry_hash},
            {"$set": {"data": entry}},
            upsert=True
        )
        return entry_hash


    def fetch_id_list(self, obj_hash: str) -> List[str]:
        doc = self.collection.find_one({"_key": obj_hash})
        if doc is None:
            raise KeyError(obj_hash)

        # Check if the list is stored in the new dictionary format (small or large)
        if doc.get("_type") == TYPE_ID_LIST_LARGE:
            return self._fetch_id_list_large(doc)
        elif doc.get("_type") == TYPE_ID_LIST_SMALL:
            return self._fetch_id_list_small(doc)

        raise ValueError("Invalid ID list format in MongoDB")

    def _fetch_id_list_small(self, data: Mapping[str, Any]) -> List[str]:
        return data["list"]

    def _fetch_id_list_large(self, data: Mapping[str, Any]) -> List[str]:
        entries = []
        for key, subset_hash in data.items():
            if key == "_type":
                continue

            subset_doc = self.collection.find_one({"_key": subset_hash})
            if subset_doc is None:
                raise KeyError(subset_hash)

            # Subsets are stored as lists in "list" field, similar to a small list
            subset = subset_doc["list"]
            entries.extend([key + s for s in subset])
        return entries

    def insert_id_list(self, entries: List[str]) -> str:
        if len(entries) <= MAX_COMPACT_LIST_SIZE:
            return self._insert_id_list_small(entries)
        else:
            return self._insert_id_list_large(entries)

    def _insert_id_list_small(self, entries: List[str]) -> str:
        data = {
            "_type": TYPE_ID_LIST_SMALL,
            "list": entries
        }

        # reuse the same hash function as DBM for constitency
        data_hash = sha256_hash(encode_dict_str(data))

        self.collection.update_one(
            {"_key": data_hash},
            {"$set": data},
            upsert=True
        )
        return data_hash

    def _insert_id_list_large(self, entries: List[str]) -> str:
        subsets = defaultdict(list)
        for x in entries:
            key, val = x[:KEY_LENGTH], x[KEY_LENGTH:]
            subsets[key].append(val)

        # insert subsets, and track them for the superset
        superset = {"_type": TYPE_ID_LIST_LARGE}
        for key, val in subsets.items():
            list_hash = sha256_hash(encode_list_str(val))
            # Store subset. We use "list" field to store the actual list of suffixes.
            self.collection.update_one(
                {"_key": list_hash},
                {"$set": {"list": val}},
                upsert=True
            )
            superset[key] = list_hash

        # now create and store the superset
        superset_hash = sha256_hash(encode_dict_str(superset))
        self.collection.update_one(
            {"_key": superset_hash},
            {"$set": superset},
            upsert=True
        )
        return superset_hash
