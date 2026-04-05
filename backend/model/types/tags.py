from dataclasses import dataclass
from typing import List

from db.abc.db import DBInterface


@dataclass
class Commit:
    author: str
    description: str
    head: StateTreeRootNode
    parent_commit_hash: str

    def write(self, backend: DBInterface) -> str:
        head_hash = self.head.write(backend)
        return backend.insert_obj({
            "author": self.author,
            "description": self.description,
            "head": head_hash,
            "parent_commit_hash": self.parent_commit_hash,
        })

    @staticmethod
    def read(backend: DBInterface, hash: str) -> 'Commit':
        raw_commit = backend.fetch_obj(hash)
        head = StateTreeRootNode.read(backend, raw_commit["head"])
        return Commit(
            author=raw_commit["author"],
            description=raw_commit["description"],
            head=head,
            parent_commit_hash=raw_commit["parent_commit_hash"],
        )


@dataclass
class StateTreeRootNode:
    categories: List[str]
    tokens: List[str]

    def write(self, backend: DBInterface) -> str:
        cat_list_hash = backend.insert_id_list(self.categories)
        tok_list_hash = backend.insert_id_list(self.tokens)
        return backend.insert_obj({
            "categories": cat_list_hash,
            "tokens": tok_list_hash,
        })

    @staticmethod
    def read(backend: DBInterface, hash: str) -> 'StateTreeRootNode':
        raw_head = backend.fetch_obj(hash)
        categories = backend.fetch_id_list(raw_head["categories"])
        tokens = backend.fetch_id_list(raw_head["tokens"])
        return StateTreeRootNode(
            categories=categories,
            tokens=tokens,
        )
