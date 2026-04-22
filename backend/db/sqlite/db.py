import sqlite3
import os
from contextlib import contextmanager
from typing import Generator, Dict, Any, List, cast, Optional

from db.abc.db import DBInterface
from db.abc.constants import MAX_COMPACT_LIST_SIZE, TYPE_KEY, TypeIDs
from db.util.hash import sha256_hash
from db.util.simple_bson import bson_encode, bson_decode, BSON_SUPPORTED_TYPES
from db.util.list_subset import strip_type, build_superset
from util.log import log_debug


class SQLiteDB(DBInterface):
    """
    Persistent Database implementation using SQLite.
    Provides a robust, single-file relational database backend.
    """
    def __init__(self, filename: str):
        """
        :param filename: Path to the SQLite database file.
        """
        super().__init__()
        self.filename = filename
        self._initialize_db()

    def _initialize_db(self):
        with self.get_connection() as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value BLOB)"
            )
            con.commit()

    @contextmanager
    def get_connection(self, existing_con: Optional[sqlite3.Connection] = None) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager to provide a thread-safe connection to the SQLite database.
        Ensures the connection is closed after each operation.
        """
        if existing_con:
            yield existing_con
            return

        con = sqlite3.connect(self.filename)
        try:
            yield con
        finally:
            con.close()

    def close(self):
        log_debug("DB", "Closing SQLiteDB")
        # context manager manages sqlite connection per operation, so no need to close
        pass

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "db-type": "SQLite",
            "db-path": self.filename,
            "db-file-size": os.path.getsize(self.filename),
        }


    def _generic_fetch_decode(self, obj_hashes: List[str], ex_con: Optional[sqlite3.Connection] = None) -> List[BSON_SUPPORTED_TYPES]:
        if not obj_hashes:
            return []
        with self.get_connection(ex_con) as con:
            placeholders = ",".join(["?"] * len(obj_hashes))
            cur = con.execute(f"SELECT key, value FROM kv WHERE key IN ({placeholders})", obj_hashes)
            docs = {row[0]: row[1] for row in cur.fetchall()}
            raw_data = []
            for key in obj_hashes:
                if key not in docs:
                    raise KeyError(key)
                raw_data.append(docs[key])
        return [
            bson_decode(cast(bytes, d))
            for d in raw_data
        ]

    def _generic_insert_encode(self, entries: List[BSON_SUPPORTED_TYPES], con: Optional[sqlite3.Connection] = None) -> List[str]:
        # reuse the same hash function as DBM for consistency
        bsons = [bson_encode(e) for e in entries]
        hashes = [sha256_hash(b) for b in bsons]
        self._generic_insert(hashes, bsons, con)
        return hashes

    def _generic_insert(self, keys: List[str], values: List[str | bytes], ex_con: Optional[sqlite3.Connection] = None) -> None:
        if not keys:
            return
        with self.get_connection(ex_con) as con:
            con.executemany(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
                zip(keys, values)
            )
            con.commit()


    def batch_fetch_obj(self, obj_hashes: List[str], **kwargs) -> List[Dict[str, Any]]:
        return cast(
            List[Dict[str, Any]],
            self._generic_fetch_decode(obj_hashes)
        )

    def batch_set_obj(self, key: List[str], val: List[Dict[str, Any]]) -> None:
        # reuse the same hash function as DBM for consistency
        bsons = [bson_encode(e) for e in val]
        self._generic_insert(key, bsons)

    def batch_insert_obj(self, entries: List[Dict[str, Any]]) -> List[str]:
        return self._generic_insert_encode(entries)


    def batch_fetch_id_list(self, obj_hashes: List[str], **kwargs) -> List[List[str]]:
        # TODO: batch-operations not yet implemented, so simply loop the non-batch fetch
        with self.get_connection() as con:
            return [
                self._fetch_id_list(x, con) for x in obj_hashes
            ]

    def _fetch_id_list(self, obj_hash: str, con: sqlite3.Connection) -> List[str]:
        data_dict: Dict[str, Any] = cast(
            List[Dict[str, Any]],
            self._generic_fetch_decode([obj_hash], con)
        )[0]

        if data_dict.get(TYPE_KEY) == TypeIDs.TYPE_ID_LIST_LARGE:
            return self._fetch_id_list_large(data_dict, con)
        elif data_dict.get(TYPE_KEY) == TypeIDs.TYPE_ID_LIST_SMALL:
            return self._fetch_id_list_small(data_dict)
        else:
            raise ValueError("Invalid ID list type")

    def _fetch_id_list_small(self, data: Dict[str, Any]) -> List[str]:
        return data["list"]

    def _fetch_id_list_large(self, data: Dict[str, Any], con: sqlite3.Connection) -> List[str]:
        # extract subsets from the database
        subset_hashes = strip_type(data)
        # fetch subsets from db using existing connection
        subsets = cast(List[str], cast(object, self._generic_fetch_decode(list(subset_hashes.values()), con)))
        # The subsets in large lists are expected to be just the suffixes
        return [
            key + s
            for key, subset_item in zip(subset_hashes.keys(), subsets)
            for s in subset_item
        ]

    def batch_insert_id_list(self, entries_list: List[List[str]]) -> List[str]:
        # TODO: batch-operations not yet implemented, so simply loop the non-batch insert
        with self.get_connection() as con:
            return [
                self._insert_id_list(x, con) for x in entries_list
            ]

    def _insert_id_list(self, entries: List[str], con: sqlite3.Connection) -> str:
        if len(entries) <= MAX_COMPACT_LIST_SIZE:
            return self._insert_id_list_small(entries, con)
        else:
            return self._insert_id_list_large(entries, con)

    def _insert_id_list_small(self, entries: List[str], con: sqlite3.Connection) -> str:
        data = {
            TYPE_KEY: TypeIDs.TYPE_ID_LIST_SMALL,
            "list": entries
        }
        return self._generic_insert_encode([data], con)[0]

    def _insert_id_list_large(self, entries: List[str], con: sqlite3.Connection) -> str:
        raw_data = build_superset(entries)
        hashes = self._generic_insert_encode(raw_data, con)
        # last item and therefor also hash is the superset hash
        return hashes[-1]
