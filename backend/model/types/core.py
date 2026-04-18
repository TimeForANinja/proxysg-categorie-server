from dataclasses import dataclass
from typing import Dict, List, Optional

from db.abc.db import DBInterface
from db.util.simple_bson import encode_dict_str
from model.types.category import Category
from model.types.mappings import TokenCategoryMapping, URLCategoryMapping
from model.types.token import Token
from model.types.url import URL
from model.util.diff import list_obj_diff
from routes.types.core import RestCommit


# Pointer towards the current Core Object
POINTER_CORE = "pointer_core"


@dataclass
class Core:
    """Core information for the application"""
    version: int
    branches: Dict[str, str] # map of branch name to commit hash

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
        changes_hash = backend.insert_id_list(self.head.changed_compared_to(backend, self.parent_commit_hash))
        return backend.insert_obj({
            "uuid": self.uuid,
            "author": self.author,
            "description": self.description,
            "created_at": self.created_at,
            "head": head_hash,
            "parent_commit_hash": self.parent_commit_hash,
            "ref_changed_hash": changes_hash,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'Commit':
        """read commit from db from hash"""
        raw_commit = backend.fetch_obj(obj_hash)
        head = StateTreeRootNode.read(backend, raw_commit["head"])
        changes = backend.fetch_id_list(raw_commit["ref_changed_hash"])
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
        cat_list_hash = backend.insert_id_list(self.categories)
        tok_list_hash = backend.insert_id_list(self.tokens)
        url_list_hash = backend.insert_id_list(self.urls)
        url_cat_map_hash = backend.insert_id_list(self.url_category_mappings)
        tok_cat_map_hash = backend.insert_id_list(self.token_category_mappings)
        return backend.insert_obj({
            "categories": cat_list_hash,
            "tokens": tok_list_hash,
            "urls": url_list_hash,
            "url_category_mappings": url_cat_map_hash,
            "token_category_mappings": tok_cat_map_hash,
        })

    @staticmethod
    def read(backend: DBInterface, obj_hash: str) -> 'StateTreeRootNode':
        raw_head = backend.fetch_obj(obj_hash)
        categories = backend.fetch_id_list(raw_head["categories"])
        tokens = backend.fetch_id_list(raw_head["tokens"])
        urls = backend.fetch_id_list(raw_head["urls"])
        url_category_mappings = backend.fetch_id_list(raw_head["url_category_mappings"])
        token_category_mappings = backend.fetch_id_list(raw_head["token_category_mappings"])
        return StateTreeRootNode(
            categories=categories,
            tokens=tokens,
            urls=urls,
            url_category_mappings=url_category_mappings,
            token_category_mappings=token_category_mappings,
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
            u.id: u for u in [
                URL.read(backend, url_hash)
                for url_hash in self.urls
            ]
        }

    def category_lut(self, backend: DBInterface) -> Dict[str, Category]:
        return {
            c.id: c for c in [
                Category.read(backend, cat_hash)
                for cat_hash in self.categories
            ]
        }

    def token_lut(self, backend: DBInterface) -> Dict[str, Token]:
        return {
            c.id: c for c in [
                Token.read(backend, tok_hash)
                for tok_hash in self.tokens
            ]
        }
