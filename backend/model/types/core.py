import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, cast

from db.abc.constants import TYPE_KEY, TypeIDs
from db.abc.db import DBInterface
from model.types.category import Category
from model.types.mappings import TokenCategoryMapping, URLCategoryMapping
from model.types.token import Token
from model.types.url import URL
from model.util.diff import list_obj_diff
from routes.types.core import RestCommit
from util.simple_bson import bson_encode, bson_decode

# Pointer towards the current Core Object
POINTER_CORE = "pointer_core"


@dataclass
class Core:
    """Core information for the application"""
    version: int
    branches: Dict[str, str] # map of branch name to commit hash

    def write(self, backend: DBInterface):
        # same as insert_obj, but with predefined key
        entry_bson = bson_encode({
            TYPE_KEY: TypeIDs.TYPE_ID_CORE,
            "version": self.version,
            "branches": self.branches,
        })
        backend.batch_insert_kv([POINTER_CORE], [entry_bson])

    @staticmethod
    def read(backend: DBInterface) -> 'Core':
        raw_core_str = backend.batch_fetch_kv([POINTER_CORE])[0]
        raw_core = bson_decode(cast(bytes, raw_core_str))
        return Core(
            version=raw_core["version"],
            branches=raw_core["branches"],
        )


@dataclass
class Commit:
    uuid: str
    author: str
    description: str
    created_at: int
    head: StateTreeRootNode # Root Node holding all Data
    parent_commit_hash: Optional[str] # Hash of the parent commit, None if it's the root commit
    ref_changed_uuid: List[str] # uuid of changed objects - allows faster filtering in hindsight

    def to_rest(self, backend: DBInterface) -> RestCommit:
        parent_uuid: Optional[str] = None
        if self.parent_commit_hash:
            parent_uuid = Commit.read(backend, self.parent_commit_hash).uuid

        return RestCommit(
            uuid=self.uuid,
            author=self.author,
            description=self.description,
            created_at=self.created_at,
            parent_commit=parent_uuid,
        )

    def write(self, backend: DBInterface) -> str:
        """write commit to db and return hash"""
        head_hash = self.head.write(backend)
        changes_hash = backend.batch_insert_id_list([
            self.head.changed_compared_to(backend, self.parent_commit_hash),
        ])[0]
        return backend.batch_insert_obj([{
            TYPE_KEY: TypeIDs.TYPE_ID_COMMIT,
            "uuid": self.uuid,
            "author": self.author,
            "description": self.description,
            "created_at": self.created_at,
            "head": head_hash,
            "parent_commit_hash": self.parent_commit_hash,
            "ref_changed_hash": changes_hash,
        }])[0]

    @staticmethod
    def new(author: str, description: str, parent: Optional[str]) -> 'Commit':
        return Commit(
                uuid=str(uuid.uuid4()),
                author=author,
                description=description,
                created_at=int(datetime.now().timestamp()),
                head=StateTreeRootNode(
                    categories=[],
                    tokens=[],
                    urls=[],
                    url_category_mappings=[],
                    token_category_mappings=[],
                ),
                parent_commit_hash=parent,
                ref_changed_uuid=[],
            )

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Commit':
        """read commit from db from hash"""
        raw_commit = backend.batch_fetch_obj([obj_hash])[0]
        head = StateTreeRootNode.read(backend, raw_commit["head"])
        changes = backend.batch_fetch_id_list([raw_commit["ref_changed_hash"]])[0]
        return Commit(
            uuid=raw_commit["uuid"],
            author=raw_commit["author"],
            description=raw_commit["description"],
            created_at=raw_commit["created_at"],
            head=head,
            parent_commit_hash=raw_commit["parent_commit_hash"],
            ref_changed_uuid=changes,
        )

    def write_branch(self, backend: DBInterface, branch: str):
        """write commit to db, and then update branch tag"""
        commit_hash = self.write(backend)
        core = Core.read(backend)
        core.branches[branch] = commit_hash
        core.write(backend)

    @staticmethod
    def read_branch(backend: DBInterface, branch: str) -> 'Commit':
        """read commit from db by branch tag"""
        core = Core.read(backend)
        branch_hash = core.branches[branch]
        return Commit.read(backend, branch_hash)


@dataclass
class StateTreeRootNode:
    # List of related object Hashes
    categories: List[str]
    tokens: List[str]
    urls: List[str]
    url_category_mappings: List[str]
    token_category_mappings: List[str]

    def write(self, backend: DBInterface) -> str:
        id_list_hashes = backend.batch_insert_id_list([
            self.categories,
            self.tokens,
            self.urls,
            self.url_category_mappings,
            self.token_category_mappings
        ])
        return backend.batch_insert_obj([{
            TYPE_KEY: TypeIDs.TYPE_ID_STATE_TREE,
            "categories": id_list_hashes[0],
            "tokens": id_list_hashes[1],
            "urls": id_list_hashes[2],
            "url_category_mappings": id_list_hashes[3],
            "token_category_mappings": id_list_hashes[4],
        }])[0]

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'StateTreeRootNode':
        raw_head = backend.batch_fetch_obj([obj_hash])[0]
        id_lists = backend.batch_fetch_id_list([
            raw_head["categories"],
            raw_head["tokens"],
            raw_head["urls"],
            raw_head["url_category_mappings"],
            raw_head["token_category_mappings"],
        ])
        return StateTreeRootNode(
            categories=id_lists[0],
            tokens=id_lists[1],
            urls=id_lists[2],
            url_category_mappings=id_lists[3],
            token_category_mappings=id_lists[4],
        )

    def changed_compared_to(self, backend: DBInterface, other_hash: Optional[str]) -> List[str]:
        changed_uuid = set()
        comp = Commit.read(backend, other_hash) if other_hash else None

        # compare all objects
        changed_uuid.update(list_obj_diff(
            backend,
            self.urls, comp.head.urls if comp else None,
            URL, ["id"]
        ))
        changed_uuid.update(list_obj_diff(
            backend,
            self.tokens, comp.head.tokens if comp else None,
            Token, ["id"]
        ))
        changed_uuid.update(list_obj_diff(
            backend,
            self.categories, comp.head.categories if comp else None,
            Category, ["id"]
        ))
        # compare mappings
        changed_uuid.update(list_obj_diff(
            backend,
            self.token_category_mappings, comp.head.token_category_mappings if comp else None,
            TokenCategoryMapping, ["token_id", "category_id"]
        ))
        changed_uuid.update(list_obj_diff(
            backend,
            self.url_category_mappings, comp.head.url_category_mappings if comp else None,
            URLCategoryMapping, ["url_id", "category_id"]
        ))

        return list(changed_uuid)

    def url_lut(self, backend: DBInterface) -> Dict[str, URL]:
        return {
            u.id: u
            for u in URL.batch_read(backend, self.urls)
        }

    def category_lut(self, backend: DBInterface) -> Dict[str, Category]:

        return {
            c.id: c
            for c in Category.batch_read(backend, self.categories)
        }

    def token_lut(self, backend: DBInterface) -> Dict[str, Token]:
        return {
            c.id: c
            for c in Token.batch_read(backend, self.tokens)
        }
