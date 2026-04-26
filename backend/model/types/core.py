import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from db.abc.constants import TYPE_KEY, TypeIDs
from db.abc.db import DBInterface
from model.types.category import Category, PREDEFINED_CATEGORIES
from model.types.mappings import TokenCategoryMapping, URLCategoryMapping, ChildCategoryMapping
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
    bc_categories: List[str] # hashes of bc categories
    token_usages: List[str] # hashes of token usage

    # TODO: switch to something like this instead of read/write to prevent race conditions
    #@staticmethod
    #def update(backend: DBInterface, ca: Callable[[Core], None]):
    #    c = Core.read(backend)
    #    ca(c)
    #    c._write(backend)

    def write(self, backend: DBInterface):
        # same as insert_obj, but with predefined key
        list_hashes = backend.batch_insert_id_list([self.bc_categories, self.token_usages])
        backend.batch_set_obj([POINTER_CORE], [{
            TYPE_KEY: TypeIDs.TYPE_ID_CORE,
            "version": self.version,
            "branches": self.branches,
            "bc_categories": list_hashes[0],
            "token_usages": list_hashes[1],
        }])

    @staticmethod
    def read(backend: DBInterface) -> 'Core':
        raw_core = backend.batch_fetch_obj(
            [POINTER_CORE],
            # required when run multithreaded since the key is non-unique
            bypass_cache=True,
        )[0]
        id_lists = backend.batch_fetch_id_list([raw_core["bc_categories"], raw_core["token_usages"]])
        return Core(
            version=raw_core["version"],
            branches=raw_core["branches"],
            bc_categories=id_lists[0],
            token_usages=id_lists[1],
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
    def new(
            author: str,
            description: str,
            parent: Optional[str] = None,
            head: Optional[StateTreeRootNode] = None
    ) -> 'Commit':
        return Commit(
                uuid=str(uuid.uuid4()),
                author=author,
                description=description,
                created_at=int(datetime.now().timestamp()),
                head=head or StateTreeRootNode(
                    categories=[],
                    tokens=[],
                    urls=[],
                    url_category_mappings=[],
                    token_category_mappings=[],
                     child_category_mappings=[],
                ),
                parent_commit_hash=parent,
                ref_changed_uuid=[],
            )

    @staticmethod
    def read_from_uuid(backend: DBInterface, commit_uuid: str) -> Optional['Commit']:
        """search and read a commit by it's uuid"""
        core = Core.read(backend)

        # track hashes we've already visited
        visited_hashes = set()

        # Since we don't have a global index, we search through all branches one by one
        for branch_name in core.branches:
            # load first commit
            uut = core.branches[branch_name]
            # then iterate through all parent commits in the linked list
            while uut:
                if uut in visited_hashes:
                    # early exit if we already visited this commit (e.g., from a different branch)
                    break

                # load commit and check if it's our target
                c = Commit.read(backend, uut)
                if c.uuid == commit_uuid:
                    return c

                # prepare for next iteration
                visited_hashes.add(uut)
                uut = c.parent_commit_hash
        return None

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
    child_category_mappings: List[str]

    def write(self, backend: DBInterface) -> str:
        id_list_hashes = backend.batch_insert_id_list([
            self.categories,
            self.tokens,
            self.urls,
            self.url_category_mappings,
            self.token_category_mappings,
            self.child_category_mappings
        ])
        return backend.batch_insert_obj([{
            TYPE_KEY: TypeIDs.TYPE_ID_STATE_TREE,
            "categories": id_list_hashes[0],
            "tokens": id_list_hashes[1],
            "urls": id_list_hashes[2],
            "url_category_mappings": id_list_hashes[3],
            "token_category_mappings": id_list_hashes[4],
            "child_category_mappings": id_list_hashes[5],
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
            raw_head["child_category_mappings"],
        ])
        return StateTreeRootNode(
            categories=id_lists[0],
            tokens=id_lists[1],
            urls=id_lists[2],
            url_category_mappings=id_lists[3],
            token_category_mappings=id_lists[4],
            child_category_mappings=id_lists[5],
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
            Category, ["id"],
            exclude=[x.id for x in PREDEFINED_CATEGORIES],
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
        changed_uuid.update(list_obj_diff(
            backend,
            self.child_category_mappings, comp.head.child_category_mappings if comp else None,
            ChildCategoryMapping, ["category_id", "child_category_id"]
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
