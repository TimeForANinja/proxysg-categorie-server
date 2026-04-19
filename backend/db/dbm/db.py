import dbm
import os
from contextlib import contextmanager
from typing import Generator, Dict, Any, List, cast, Optional

from db.abc.db import DBInterface
from db.abc.constants import MAX_COMPACT_LIST_SIZE, TYPE_KEY, TypeIDs
from db.util.simple_bson import bson_encode, bson_decode, BSON_SUPPORTED_TYPES
from db.util.hash import sha256_hash
from db.util.list_subset import strip_type, build_superset
from util.log import log_debug


class DBMDB(DBInterface):
    """
    Persistent Database implementation using the Python `dbm` module.
    Ideal for simple, file-based key-value storage without external dependencies.
    """
    def __init__(self, filename):
        """
        :param filename: Path to the DBM database file.
        """
        super().__init__()
        self.filename = filename

    @contextmanager
    def get_connection(self) -> Generator[dbm._Database, None, None]:
        """
        Context manager to handle the open/close actions of the DBM file for each operation.
        """
        with dbm.open(self.filename, "c") as db:
            yield db

    def close(self):
        log_debug("DB", "Closing DBMDB")
        # dbm gets opened and closed for each connection, so no need to close
        pass

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "db-type": "DBM",
            "db-path": self.filename,
            "db-file-size": os.path.getsize(self.filename),
        }


    @contextmanager
    def _get_con(self, con: Optional[dbm._Database] = None) -> Generator[dbm._Database, None, None]:
        """Utility function to handle the connection argument"""
        if con:
            yield con
            return

        # No connection provided, open a new one
        with self.get_connection() as c:
            yield c


    def _generic_fetch_decode(self, keys: List[str], con: Optional[dbm._Database] = None) -> List[BSON_SUPPORTED_TYPES]:
        return [
            bson_decode(cast(bytes, data))
            for data in self.batch_fetch_kv(keys, con)
        ]

    def _generic_insert_encode(self, entries: List[BSON_SUPPORTED_TYPES], con: Optional[dbm._Database] = None) -> List[str]:
        # reuse the same hash function as DBM for consistency
        bsons = [bson_encode(e) for e in entries]
        hashes = [sha256_hash(b) for b in bsons]
        self.batch_insert_kv(hashes, bsons, con)
        return hashes


    def batch_fetch_kv(self, keys: List[str], existing_con: Optional[dbm._Database] = None) -> List[str | bytes]:
        with self._get_con(existing_con) as con:
            return [con[key] for key in keys]

    def batch_insert_kv(self, keys: List[str], values: List[str | bytes], existing_con: Optional[dbm._Database] = None) -> None:
        with self._get_con(existing_con) as con:
            for key, value in zip(keys, values):
                con[key] = value


    def batch_fetch_obj(self, obj_hashes: List[str]) -> List[Dict[str, Any]]:
        return cast(List[Dict[str, Any]], self._generic_fetch_decode(obj_hashes))

    def batch_insert_obj(self, entries: List[Dict[str, Any]]) -> List[str]:
        return self._generic_insert_encode(entries)


    def batch_fetch_id_list(self, obj_hashes: List[str]) -> List[List[str]]:
        results = []
        with self.get_connection() as con:
            # get "root" for all lists
            data_dicts = cast(List[Dict[str, Any]], self._generic_fetch_decode(obj_hashes, con))
            for data_dict, obj_hash in zip(data_dicts, obj_hashes):
                # check if the list is type small or large
                if data_dict.get(TYPE_KEY) == TypeIDs.TYPE_ID_LIST_LARGE:
                    # TODO: batch-operations for large lists not yet implemented
                    results.append(self._fetch_id_list_large(data_dict, con))
                elif data_dict.get(TYPE_KEY) == TypeIDs.TYPE_ID_LIST_SMALL:
                    results.append(self._fetch_id_list_small(data_dict))
                else:
                    raise ValueError("Invalid ID list type")
        return results

    def _fetch_id_list_small(self, data: Dict[str, Any]) -> List[str]:
        return data["list"]

    def _fetch_id_list_large(self, data: Dict[str, Any], con: dbm._Database) -> List[str]:
        # extract subsets from the database
        subset_hashes: Dict[str, str] = strip_type(data)
        # fetch subsets from db using existing connection
        subsets = cast(List[str], cast(object, self._generic_fetch_decode(list(subset_hashes.values()), con)))
        # The subsets in large lists are expected to be just the suffixes
        return [
            key + s
            for key, subset_item in zip(subset_hashes.keys(), subsets)
            for s in subset_item
        ]

    def batch_insert_id_list(self, entries_list: List[List[str]]) -> List[str]:
        results = []
        with self.get_connection() as con:
            # Insert lists one by one to the DB
            for entries in entries_list:
                # If the list is small, insert it directly to improve performance
                if len(entries) <= MAX_COMPACT_LIST_SIZE:
                    results.append(self._insert_id_list_small(entries, con))
                else:
                    # TODO: batch-operations for large lists not yet implemented
                    results.append(self._insert_id_list_large(entries, con))
        return results

    def _insert_id_list_small(self, entries: List[str], con: dbm._Database) -> str:
        data = {
            TYPE_KEY: TypeIDs.TYPE_ID_LIST_SMALL,
            "list": entries
        }
        return self._generic_insert_encode([data], con)[0]

    def _insert_id_list_large(self, entries: List[str], con: dbm._Database) -> str:
        raw_data = build_superset(entries)
        hashes = self._generic_insert_encode(raw_data, con)
        # last item and therefor also hash is the superset hash
        return hashes[-1]
