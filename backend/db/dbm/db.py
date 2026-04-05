import dbm
from collections import defaultdict
from contextlib import contextmanager
from typing import Generator, Dict, Any, List

from db.abc.db import DBInterface
from db.dbm.util.simple_bson import encode_dict_str, decode_dict_str, encode_list_str, decode_list_str
from db.dbm.util.hash import sha256_hash


KEY_LENGTH = 2


class DBM_DB(DBInterface):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    @contextmanager
    def get_connection(self) -> Generator[dbm._Database]:
        with dbm.open(self.filename, "c") as db:
            yield db

    def close(self):
        # dbm get's opened and closed for each connection, so no need to close
        pass

    def fetch_kv(self, key: str) -> str:
        with self.get_connection() as con:
            return con[key]

    def insert_kv(self, key: str, value: str):
        with self.get_connection() as con:
            con[key] = value

    def fetch_obj(self, hash: str) -> Dict[Any, Any]:
        # fetch from db
        with self.get_connection() as con:
            obj_bson = con[hash]
            obj = decode_dict_str(obj_bson)
            return obj

    def insert_obj(self, entry: Dict[Any, Any]) -> str:
        with self.get_connection() as con:
            entry_bson = encode_dict_str(entry)
            entry_hash = sha256_hash(entry_bson)
            if entry_hash not in con:
                con[entry_hash] = entry_bson
            return entry_hash

    def fetch_id_list(self, hash: str) -> List[str]:
        entries = []
        # fetch from db
        with self.get_connection() as con:
            superset_bson = con[hash]
            superset = decode_dict_str(superset_bson)
            for key, val in superset.items():
                subset_bson = con[val]
                subset = decode_list_str(subset_bson)
                entries.extend([key + s for s in subset])
        return entries

    def insert_id_list(self, entries: List[str]) -> str:
        # sort into subsets
        subsets = defaultdict(list)
        for x in entries:
            key, val = x[:KEY_LENGTH], x[KEY_LENGTH:]
            subsets[key].append(val)

        with self.get_connection() as con:
            # insert subsets, and track them for the superset
            superset = {}
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
