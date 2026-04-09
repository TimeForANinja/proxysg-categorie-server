from dataclasses import dataclass
from typing import Dict, List as tList

from marshmallow.fields import List, String
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from db.dbm.util.simple_bson import encode_dict_str
from util.schema import desc, to_field

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


@dataclass
class StateTreeRootNode:
    categories: tList[str] = to_field(List(
        String(required=True, metadata=desc('Category ID')),
        required=True,
        metadata=desc('List of all Categories in this Version'),
    ))
    tokens: tList[str] = to_field(List(
        String(required=True, metadata=desc('Token ID')),
        required=True,
        metadata=desc('List of all Tokens in this Version'),
    ))

    def write(self, backend: DBInterface) -> str:
        cat_list_hash = backend.insert_id_list(self.categories)
        tok_list_hash = backend.insert_id_list(self.tokens)
        return backend.insert_obj({
            "categories": cat_list_hash,
            "tokens": tok_list_hash,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'StateTreeRootNode':
        raw_head = backend.fetch_obj(obj_hash)
        categories = backend.fetch_id_list(raw_head["categories"])
        tokens = backend.fetch_id_list(raw_head["tokens"])
        return StateTreeRootNode(
            categories=categories,
            tokens=tokens,
        )


state_tree_root_node_schema = class_schema(StateTreeRootNode)()
