from typing import Dict, Any, List, Mapping
from pymongo import MongoClient, UpdateOne

from db.abc.db import DBInterface
from db.abc.constants import MAX_COMPACT_LIST_SIZE, TYPE_KEY, TypeIDs
from db.util.simple_bson import bson_encode
from db.util.hash import sha256_hash
from db.util.list_subset import strip_type, build_superset
from util.log import log_debug


class MongoDB(DBInterface):
    """
    Persistent Database implementation using MongoDB.
    Suitable for distributed environments or when high availability and scalability are required.
    """
    def __init__(self, host: str, port: int, database_name: str, username: str = None, password: str = None, auth_source: str = None, connect_direct: bool = False, collection_name: str = "data"):
        """
        Initialize the MongoDB connection and ensure indexes.

        :param host: MongoDB server hostname.
        :param port: MongoDB server port.
        :param database_name: Name of the database to use.
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param auth_source: Database to authenticate against.
        :param connect_direct: Whether to connect directly to the host.
        :param collection_name: Name of the collection for data storage.
        """
        super().__init__()
        self.client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource=auth_source,
            directConnection=connect_direct
        )
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

        # Create an index on our "_key" for fast lookups
        self.collection.create_index("_key", unique=True)

    def close(self):
        log_debug("DB", "Closing MongoDB")
        self.client.close()

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "db-type": "MongoDB",
            "db-path": self.client.address,
        }


    def _generic_fetch(self, keys: List[str]) -> List[Any]:
        if not keys:
            return []
        docs = {
            # mongodb already stores data as dict, so no conversion required
            doc["_key"]: doc["data"]
            for doc
            in self.collection.find({"_key": {"$in": keys}})
        }
        results = []
        for key in keys:
            if key not in docs:
                raise KeyError(key)
            results.append(docs[key])
        return results

    def _generic_insert_hash(self, values: List[Any]) -> List[str]:
        # reuse the same hash function as DBM for consistency
        hashes = [sha256_hash(bson_encode(v)) for v in values]
        self._generic_insert(hashes, values)
        return hashes

    def _generic_insert(self, keys: List[str], values: List[Any]) -> None:
        if not keys:
            return
        operations = [
            UpdateOne(
                {"_key": key},
                # mongodb already stores data as dict, so no conversion required.
                # Stores in the "data" field to support additional types like List.
                {"$set": {"data": value}},
                upsert=True
            )
            for key, value in zip(keys, values)
        ]
        if operations:
            self.collection.bulk_write(operations)


    def batch_fetch_obj(self, obj_hashes: List[str], **kwargs) -> List[Dict[str, Any]]:
        return self._generic_fetch(obj_hashes)

    def batch_set_obj(self, key: List[str], val: List[Dict[str, Any]]) -> None:
        self._generic_insert(key, val)

    def batch_insert_obj(self, entries: List[Dict[str, Any]]) -> List[str]:
        return self._generic_insert_hash(entries)


    def batch_fetch_id_list(self, obj_hashes: List[str], **kwargs) -> List[List[str]]:
        # TODO: batch-operations not yet implemented, so simply loop the non-batch fetch
        return [
            self._fetch_id_list(x) for x in obj_hashes
        ]

    def _fetch_id_list(self, obj_hash: str) -> List[str]:
        doc: Dict[str, Any] = self._generic_fetch([obj_hash])[0]

        # Check if the list is stored in the new dictionary format (small or large)
        if doc.get(TYPE_KEY) == TypeIDs.TYPE_ID_LIST_LARGE:
            return self._fetch_id_list_large(doc)
        elif doc.get(TYPE_KEY) == TypeIDs.TYPE_ID_LIST_SMALL:
            return self._fetch_id_list_small(doc)
        else:
            raise ValueError("Invalid ID list format in MongoDB")

    def _fetch_id_list_small(self, data: Mapping[str, Any]) -> List[str]:
        return data["list"]

    def _fetch_id_list_large(self, data: Mapping[str, Any]) -> List[str]:
        # extract subsets from the database
        subset_hashes = strip_type(dict(data))
        # fetch subsets from db using existing connection
        subsets = self._generic_fetch(list(subset_hashes.values()))
        # The subsets in large lists are expected to be just the suffixes
        return [
            key + s
            for key, subset_item in zip(subset_hashes.keys(), subsets)
            for s in subset_item
        ]

    def batch_insert_id_list(self, entries_list: List[List[str]]) -> List[str]:
        # TODO: batch-operations not yet implemented, so simply loop the non-batch insert
        return [
            self._insert_id_list(x) for x in entries_list
        ]

    def _insert_id_list(self, entries: List[str]) -> str:
        if len(entries) <= MAX_COMPACT_LIST_SIZE:
            return self._insert_id_list_small(entries)
        else:
            return self._insert_id_list_large(entries)

    def _insert_id_list_small(self, entries: List[str]) -> str:
        data = {
            TYPE_KEY: TypeIDs.TYPE_ID_LIST_SMALL,
            "list": entries
        }
        return self._generic_insert_hash([data])[0]

    def _insert_id_list_large(self, entries: List[str]) -> str:
        raw_data = build_superset(entries)
        hashes = self._generic_insert_hash(raw_data)
        # last item and therefor also hash is the superset hash
        return hashes[-1]
