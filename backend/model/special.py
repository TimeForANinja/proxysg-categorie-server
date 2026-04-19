from typing import List, Dict, Optional

from db.abc.db import DBInterface
from model.types.category import Category
from model.types.core import Core
from model.util.build_localdb import build_localdb
from model.util.error import CanError, ModelError
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping
from routes.types.core import RestCommit
from routes.schemas.url import RestURLDetail
from model.types.core import Commit
from routes.types.token import RestTokenDetail
from routes.types.url import RestConstrainedCategory
from util.branch_names import BRANCH_PROD


ERROR_NOT_FOUND = ModelError("Not Found")


class SpecialModel:
    """Special Read-Only Routes useful for the Frontend"""
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_commits(
            self,
            branch: str,
            filter_uuid: Optional[List[str]],
    ) -> List[RestCommit]:
        """
        Fetch a list of recent Commits by Name

        :param branch: The branch to fetch commits from
        :param filter_uuid: The UUIDs to filter by, or None to ignore this filter
        :return: A (filtered) list of Commits
        """
        commits = []

        # load first / current commit
        core = Core.read(self.backend)
        uut_hash = core.branches[branch]

        # Iterate over all elements in our linked list
        while uut_hash is not None:
            c = Commit.read(self.backend, uut_hash)

            # check our filters (if provided) and add to our list if we match
            if (
                filter_uuid is None
                or
                any(x in c.ref_changed_uuid for x in filter_uuid)
            ):
                commits.append(c.to_rest(self.backend))

            # update our pointer to the next commit
            uut_hash = c.parent_commit_hash

        return commits


    def list_branches(self) -> List[str]:
        """Fetch a list of all Branches"""
        core = Core.read(self.backend)
        return list(core.branches.keys())


    def fetch_categories(self, branch: str) -> List[Category]:
        """Fetch a list of all Categories"""
        head_commit = Commit.read_branch(self.backend, branch)
        category_lut = head_commit.head.category_lut(self.backend)
        return list(category_lut.values())

    def fetch_url_list(self, branch: str) -> List[RestURLDetail]:
        """Fetch a list of all URLs"""
        head_commit = Commit.read_branch(self.backend, branch)

        # Fetch LUTs
        url_lut = head_commit.head.url_lut(self.backend)
        category_lut = head_commit.head.category_lut(self.backend)

        # create base-objects for every URL
        data: Dict[str, RestURLDetail] = {
            url_id: RestURLDetail(
                url=url_lut[url_id],
                categories=[],
            )
            for url_id in url_lut
        }

        # fill our category properties based on our mappings
        mappings = URLCategoryMapping.batch_read(self.backend, head_commit.head.url_category_mappings)
        for mapping in mappings:
            data[mapping.url_id].categories.append(
                RestConstrainedCategory(
                    category=category_lut[mapping.category_id],
                    constraint=mapping.constraint,
                )
            )

        return list(data.values())

    def fetch_tokens(self, branch: str) -> List[RestTokenDetail]:
        """Fetch a list of all Tokens"""
        head_commit = Commit.read_branch(self.backend, branch)

        # Fetch LUTs
        token_lut = head_commit.head.token_lut(self.backend)
        category_lut = head_commit.head.category_lut(self.backend)

        # create base-objects for every Token
        data: Dict[str, RestTokenDetail] = {
            token_id: RestTokenDetail(
                token=token_lut[token_id],
                categories=[],
            )
            for token_id in token_lut
        }

        # fill our category properties based on our mappings
        mappings = TokenCategoryMapping.batch_read(self.backend, head_commit.head.token_category_mappings)
        for mapping in mappings:
            data[mapping.token_id].categories.append(
                category_lut[mapping.category_id]
            )

        return list(data.values())


    def compile_categories(self, token_val: str) -> CanError[str]:
        commit = Commit.read_branch(self.backend, BRANCH_PROD)

        # fetch all tokens and search for our token by value
        token_lut = commit.head.token_lut(self.backend)
        token = next((t for t in token_lut.values() if t.token_value == token_val), None)
        if not token:
            return None, ERROR_NOT_FOUND

        # TODO: update token usage

        categories = commit.head.category_lut(self.backend)
        urls = commit.head.url_lut(self.backend)
        cat_mappings = TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings)
        url_mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)

        return build_localdb(token, urls, categories, cat_mappings, url_mappings), None
