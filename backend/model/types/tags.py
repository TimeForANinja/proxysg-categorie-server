from dataclasses import dataclass
from typing import Optional

from marshmallow.fields import String, Nested
from marshmallow_dataclass import class_schema

from db.abc.db import DBInterface
from model.types.core import Core, StateTreeRootNode, state_tree_root_node_schema
from util.schema import desc, to_field


@dataclass
class Commit:
    author: str = to_field(String(required=True, metadata=desc('Username of the author')))
    description: str = to_field(String(required=True, metadata=desc('Description of the commit')))
    head: StateTreeRootNode = to_field(Nested(
        state_tree_root_node_schema,
        required=True,
        metadata=desc('Head of the commit')
    ))
    parent_commit_hash: Optional[str] = to_field(String(
        required=False,
        metadata=desc('Hash of the parent commit, or None if it is the root commit'),
    ))

    def write(self, backend: DBInterface) -> str:
        head_hash = self.head.write(backend)
        return backend.insert_obj({
            "author": self.author,
            "description": self.description,
            "head": head_hash,
            "parent_commit_hash": self.parent_commit_hash,
        })

    def write_branch(self, backend: DBInterface, branch_tag: str):
        commit_hash = self.write(backend)
        core = Core.read(backend)
        core.branches[branch_tag] = commit_hash
        core.write(backend)

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Commit':
        raw_commit = backend.fetch_obj(obj_hash)
        head = StateTreeRootNode.read(backend, raw_commit["head"])
        return Commit(
            author=raw_commit["author"],
            description=raw_commit["description"],
            head=head,
            parent_commit_hash=raw_commit["parent_commit_hash"],
        )
    @staticmethod
    def read_branch(backend: DBInterface, branch_tag: str) -> 'Commit':
        core = Core.read(backend)
        user_tag = core.branches[branch_tag]
        return Commit.read(backend, user_tag)


commit_schema = class_schema(Commit)()
