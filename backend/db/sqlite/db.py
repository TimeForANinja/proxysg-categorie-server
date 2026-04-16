import sqlite3
from collections import defaultdict
from contextlib import contextmanager
from typing import Generator, Dict, Any, List

from db.abc.db import DBInterface
from db.abc.constants import KEY_LENGTH, MAX_COMPACT_LIST_SIZE, TYPE_ID_LIST_SMALL, TYPE_ID_LIST_LARGE
from db.dbm.util.hash import sha256_hash
from db.dbm.util.simple_bson import encode_dict_str, decode_dict_str, decode_list_str, encode_list_str


class SQLiteDB(DBInterface):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with self.get_connection() as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value BLOB)"
            )
            con.commit()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        con = sqlite3.connect(self.db_path)
        try:
            yield con
        finally:
            con.close()

    def close(self):
        # sqlite connection is managed by context manager per operation
        pass


    def has_key(self, key: str) -> bool:
        with self.get_connection() as con:
            cur = con.execute("SELECT 1 FROM kv WHERE key = ?", (key,))
            return cur.fetchone() is not None


    def fetch_kv(self, key: str) -> str | bytes:
        with self.get_connection() as con:
            cur = con.execute("SELECT value FROM kv WHERE key = ?", (key,))
            row = cur.fetchone()
            if row is None:
                raise KeyError(key)
            return row[0]

    def insert_kv(self, key: str, value: str | bytes):
        with self.get_connection() as con:
            con.execute(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
                (key, value)
            )
            con.commit()


    def fetch_obj(self, obj_hash: str) -> Dict[Any, Any]:
        value = self.fetch_kv(obj_hash)
        return decode_dict_str(value)

    def insert_obj(self, entry: Dict[Any, Any]) -> str:
        # reuse the same hash function as DBM for consistency
        entry_bson = encode_dict_str(entry)
        entry_hash = sha256_hash(entry_bson)
        self.insert_kv(entry_hash, entry_bson)
        return entry_hash


    def fetch_id_list(self, obj_hash: str) -> List[str]:
        data_json = self.fetch_kv(obj_hash)
        data_dict = decode_dict_str(data_json)

        if data_dict.get("_type") == TYPE_ID_LIST_LARGE:
            return self._fetch_id_list_large(data_dict)
        elif data_dict.get("_type") == TYPE_ID_LIST_SMALL:
            return self._fetch_id_list_small(data_dict)
        else:
            raise ValueError("Invalid ID list type")

    def _fetch_id_list_small(self, data: Dict[Any, Any]) -> List[str]:
        return data["list"]

    def _fetch_id_list_large(self, data: Dict[Any, Any]) -> List[str]:
        entries = []
        for key, subset_hash in data.items():
            if key == "_type":
                continue
            subset_bson = self.fetch_kv(subset_hash)
            subset = decode_list_str(subset_bson)
            # The subsets in large lists are expected to be the suffixes
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
        data_bson = encode_dict_str(data)
        data_hash = sha256_hash(data_bson)
        self.insert_kv(data_hash, data_bson)
        return data_hash

    def _insert_id_list_large(self, entries: List[str]) -> str:
        subsets = defaultdict(list)
        for x in entries:
            key, val = x[:KEY_LENGTH], x[KEY_LENGTH:]
            subsets[key].append(val)

        superset = {"_type": TYPE_ID_LIST_LARGE}
        for key, val in subsets.items():
            subset_bson = encode_list_str(val)
            subset_hash = sha256_hash(subset_bson)
            self.insert_kv(subset_hash, subset_bson)
            superset[key] = subset_hash

        superset_json = encode_dict_str(superset)
        superset_hash = sha256_hash(superset_json)
        self.insert_kv(superset_hash, superset_json)
        return superset_hash
