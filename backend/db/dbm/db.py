import dbm
from collections import defaultdict
from contextlib import contextmanager
from typing import Generator, Dict, Any, List

from db.abc.db import DBInterface
from db.dbm.util.simple_bson import encode_dict_str, decode_dict_str, encode_list_str, decode_list_str
from db.dbm.util.hash import sha256_hash


KEY_LENGTH = 2
MAX_COMPACT_LIST_SIZE = 100


class DBMDB(DBInterface):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    @contextmanager
    def get_connection(self) -> Generator[dbm._Database]:
        with dbm.open(self.filename, "c") as db:
            yield db

    def close(self):
        # dbm gets opened and closed for each connection, so no need to close
        pass


    def has_key(self, key: str) -> bool:
        with self.get_connection() as con:
            return key in con


    def fetch_kv(self, key: str) -> str|bytes:
        with self.get_connection() as con:
            return con[key]

    def insert_kv(self, key: str, value: str|bytes):
        with self.get_connection() as con:
            con[key] = value

    def fetch_obj(self, obj_hash: str) -> Dict[Any, Any]:
        # fetch from db
        with self.get_connection() as con:
            obj_bson = con[obj_hash]
            obj = decode_dict_str(obj_bson)
            return obj

    def insert_obj(self, entry: Dict[Any, Any]) -> str:
        with self.get_connection() as con:
            entry_bson = encode_dict_str(entry)
            entry_hash = sha256_hash(entry_bson)
            if entry_hash not in con:
                con[entry_hash] = entry_bson
            return entry_hash

    def fetch_id_list(self, obj_hash: str) -> List[str]:
        # fetch from db
        with self.get_connection() as con:
            data_bson = con[obj_hash]
            data_dict = decode_dict_str(data_bson)

            # check if the list is type small or large
            if data_dict.get("_type") == "id_list_large":
                return self._fetch_id_list_large(data_dict)
            elif data_dict.get("_type") == "id_list_small":
                return self._fetch_id_list_small(data_dict)
            else:
                raise ValueError("Invalid ID list type")

    def _fetch_id_list_small(self, data: Dict[Any, Any]) -> List[str]:
        return data["list"]

    def _fetch_id_list_large(self, data: Dict[Any, Any]) -> List[str]:
        # fetch subsets from db
        with self.get_connection() as con:
            entries = []
            for key, subset_hash in data.items():
                if key == "_type":
                    continue
                subset_bson = con[subset_hash]
                subset = decode_list_str(subset_bson)
                entries.extend([key + s for s in subset])
            return entries

    def insert_id_list(self, entries: List[str]) -> str:
        # Insert a List of IDs into the DB
        # If the list is small, insert it directly to improve performance
        if len(entries) <= MAX_COMPACT_LIST_SIZE:
            return self._insert_id_list_small(entries)
        else:
            return self._insert_id_list_large(entries)

    def _insert_id_list_small(self, entries: List[str]) -> str:
        data = {
            "_type": "id_list_small",
            "list": entries
        }
        with self.get_connection() as con:
            data_bson = encode_dict_str(data)
            data_hash = sha256_hash(data_bson)
            if data_hash not in con:
                con[data_hash] = data_bson
            return data_hash

    def _insert_id_list_large(self, entries: List[str]) -> str:
        subsets = defaultdict(list)
        for x in entries:
            key, val = x[:KEY_LENGTH], x[KEY_LENGTH:]
            subsets[key].append(val)

        with self.get_connection() as con:
            # insert subsets, and track them for the superset
            superset = {"_type": "id_list_large"}
            for key, val in subsets.items():
                subset_bson = encode_list_str(val)
                subset_hash = sha256_hash(subset_bson)
                if subset_hash not in con:
                    con[subset_hash] = subset_bson
                superset[key] = subset_hash

            # now create and store the superset
            superset_bson = encode_dict_str(superset)
            superset_hash = sha256_hash(superset_bson)
            if superset_hash not in con:
                con[superset_hash] = superset_bson
            return superset_hash
