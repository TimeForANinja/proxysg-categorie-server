from dataclasses import dataclass
from typing import Dict

from db.abc.db import DBInterface
from db.dbm.util.simple_bson import encode_dict_str

POINTER_CORE = "pointer_core"

def user_branch_name(user: str) -> str:
    return f"b_user_{user}"

BRANCH_PROD = "b_prod"


@dataclass
class Core:
    version: int
    branches: Dict[str, str]

    def write(self, backend: DBInterface):
        # same as insert_obj, but with predefined key
        entry_bson = encode_dict_str({
            "version": self.version,
            "branches": self.branches,
        })
        backend.insert_kv(POINTER_CORE, entry_bson)

    @staticmethod
    def read(backend: DBInterface) -> 'Core':
        raw_core = backend.fetch_obj(POINTER_CORE)
        return Core(
            version=raw_core["version"],
            branches=raw_core["branches"],
        )
