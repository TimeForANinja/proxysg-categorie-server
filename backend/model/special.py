from typing import List, Dict, Optional

from db.abc.db import DBInterface
from model.types.category import Category
from model.types.core import Core
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping
from model.types.token import Token
from model.types.url import URL
from routes.types.core import RestCommit
from routes.schemas.url import RestURLDetail
from model.types.core import Commit
from routes.types.token import RestTokenDetail
from routes.types.url import RestConstrainedCategory


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

            # check our filters and add to our list if we match
            if (
                not filter_uuid
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
        return [
            Category.read(self.backend, h)
            for h in head_commit.head.categories
        ]

    def fetch_url_list(self, branch: str) -> List[RestURLDetail]:
        """Fetch a list of all URLs"""
        head_commit = Commit.read_branch(self.backend, branch)

        # Fetch all URL, and build LUT
        url_lut: Dict[str, URL] = {
            u.id: u for u in [
                URL.read(self.backend, url_hash)
                for url_hash in head_commit.head.urls
            ]
        }

        # Fetch all Category, and build a LUT
        category_lut: Dict[str, Category] = {
            c.id: c for c in [
                Category.read(self.backend, cat_hash)
                for cat_hash in head_commit.head.categories
            ]
        }

        # create base-objects for every URL
        data: Dict[str, RestURLDetail] = {
            url_id: RestURLDetail(
                url=url_lut[url_id],
                categories=[],
            )
            for url_id in url_lut
        }

        # fill our categories property based on our mappings
        for map_hash in head_commit.head.url_category_mappings:
            mapping = URLCategoryMapping.read(self.backend, map_hash)

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

        # Fetch all Token, and build LUT
        token_lut: Dict[str, Token] = {
            t.id: t for t in [
                Token.read(self.backend, token_hash)
                for token_hash in head_commit.head.tokens
            ]
        }

        # Fetch all Category, and build a LUT
        category_lut: Dict[str, Category] = {
            c.id: c for c in [
                Category.read(self.backend, cat_hash)
                for cat_hash in head_commit.head.categories
            ]
        }

        # create base-objects for every Token
        data: Dict[str, RestTokenDetail] = {
            token_id: RestTokenDetail(
                token=token_lut[token_id],
                categories=[],
            )
            for token_id in token_lut
        }

        # fill our categories property based on our mappings
        for map_hash in head_commit.head.token_category_mappings:
            mapping = TokenCategoryMapping.read(self.backend, map_hash)

            data[mapping.token_id].categories.append(
                category_lut[mapping.category_id]
            )

        return list(data.values())
