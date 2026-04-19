from typing import List, Dict, Optional, cast
from apiflask import APIFlask

from db.abc.db import DBInterface
from model.types.category import Category
from model.types.core import Core
from model.types.url import URL
from model.util.build_localdb import build_localdb
from model.util.error import CanError, ModelError
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping, ChildCategoryMapping
from model.util.find import find_in_lists
from routes.types.core import RestCommit
from routes.schemas.url import RestURLDetail
from model.types.core import Commit
from routes.types.token import RestTokenDetail
from routes.types.url import RestConstrainedCategory, RestTestResult
from model.types.metrics import TokenUsage, BCCategory
from util.branch_names import BRANCH_PROD
from model.util.util_query_bc import ServerCredentials, query_url, FAILED_LOOKUP
from model.util.matching import best_match_url, unnest_categories


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

        # update token usage
        TokenUsage.track_access(self.backend, token.id)

        # read data required to build localdb
        categories = commit.head.category_lut(self.backend)
        urls = commit.head.url_lut(self.backend)
        cat_mappings = TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings)
        url_mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)
        child_cat_mappings = ChildCategoryMapping.batch_read(self.backend, commit.head.child_category_mappings)

        return build_localdb(
            token, urls, categories,
            cat_mappings, url_mappings, child_cat_mappings
        ), None


    def cleanup_unused(self, branch: str) -> None:
        """Remove any unused or invalid objects from the branch"""
        commit = Commit.read_branch(self.backend, branch)

        # Cleanup Categories
        # first list Categories in use, then derive the unused categories from that
        tc_mappings = TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings)
        cat_lut = commit.head.category_lut(self.backend)
        cat_in_use = [
            c.id
            for tc_map in tc_mappings
            for c in unnest_categories(
                cat_lut[tc_map.category_id],
                cat_lut,
                ChildCategoryMapping.batch_read(self.backend, commit.head.child_category_mappings),
            )
        ]
        unused_cat_ids = set(cat_lut.keys()) - set(cat_in_use)
        unused_cats = [cat_lut[cat_id] for cat_id in unused_cat_ids]
        commit.head.categories = Category.batch_write(self.backend, unused_cats)

        # Cleanup URLs
        url_lut = commit.head.url_lut(self.backend)
        uc_mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)
        url_in_use = [
            uc_map.category_id for uc_map in uc_mappings
            if uc_map.category_id not in unused_cat_ids
        ]
        unused_url_ids = set(url_lut.keys()) - set(url_in_use)
        unused_urls = [url_lut[url_id] for url_id in unused_url_ids]
        commit.head.urls = URL.batch_write(self.backend, unused_urls)

        # Cleanup Mappings
        token_lut = commit.head.token_lut(self.backend)
        cc_mappings = ChildCategoryMapping.batch_read(self.backend, commit.head.child_category_mappings)
        ## Cleanup Token <-> Category mappings
        new_tc_mappings = [
            tc_map for tc_map in tc_mappings
            if tc_map.token_id in token_lut
                and tc_map.category_id in cat_lut
                and tc_map.category_id not in unused_cat_ids
        ]
        commit.head.token_category_mappings = TokenCategoryMapping.batch_write(self.backend, new_tc_mappings)
        ## Cleanup URL <-> Category mappings
        new_uc_mappings = [
            uc_map for uc_map in uc_mappings
            if uc_map.url_id in url_lut
                and uc_map.url_id not in unused_url_ids
                and uc_map.category_id in cat_lut
                and uc_map.category_id not in unused_cat_ids
        ]
        commit.head.url_category_mappings = URLCategoryMapping.batch_write(self.backend, new_uc_mappings)
        ## Cleanup Category <-> Category mappings
        new_cc_mappings = [
            cc_map for cc_map in cc_mappings
            if cc_map.category_id in cat_lut
                and cc_map.category_id not in unused_cat_ids
                and cc_map.child_category_id not in cat_lut
                and cc_map.child_category_id not in unused_cat_ids
        ]
        commit.head.category_category_mappings = ChildCategoryMapping.batch_write(self.backend, new_cc_mappings)

    def cleanup_core(self) -> None:
        """Cleanup objects tracked in the Core object"""
        known_tokens = set()
        known_urls = set()

        # collect all known tokens and urls from all branches
        core = Core.read(self.backend)
        for branch in core.branches.keys():
            commit = Commit.read_branch(self.backend, branch)
            known_tokens.update(commit.head.token_lut(self.backend).keys())
            known_urls.update([
                url.url
                for url in URL.batch_read(self.backend, commit.head.tokens)
            ])

        # cleanup token usage counter
        token_usage_list = TokenUsage.batch_read(self.backend)
        TokenUsage.batch_write(self.backend, [
            tu for tu in token_usage_list
            if tu.token_id in known_tokens
        ])

        # cleanup bc categories
        bc_cat_list = BCCategory.batch_read(self.backend)
        BCCategory.batch_write(self.backend, [
            bc for bc in bc_cat_list
            if bc.url_value in known_urls
        ])


    def test_url(self, app: APIFlask, url: str) -> RestTestResult:
        # 1) Normalize input to a hostname
        hostname = url.strip().lower()

        # 2) Fetch all URLs and select the best match by comparing the longest suffix that matched
        head_commit = Commit.read_branch(self.backend, BRANCH_PROD)
        url_lut = head_commit.head.url_lut(self.backend)
        best_match = best_match_url(hostname, url_lut.values())

        # 3) Fetch all categories that match the best match
        cat_lut = head_commit.head.category_lut(self.backend)
        matching_cats = []
        if best_match:
            direct_matching_cats, _ = find_in_lists(
                URLCategoryMapping.batch_read(self.backend, head_commit.head.url_category_mappings),
                head_commit.head.url_category_mappings,
                lambda m: m.url_id == cast(URL, best_match).id
            )
            matching_cats.extend([c.name for c in direct_matching_cats])
            # unnest to also get all Partents of the matched categories
            child_cat_map = ChildCategoryMapping.batch_read(self.backend, head_commit.head.child_category_mappings)
            matching_cats.extend([
                parent_cat.name
                for c in direct_matching_cats
                for parent_cat in unnest_categories(
                    cat_lut[c.category_id],
                    cat_lut,
                    child_cat_map,
                    True,
                )
            ])

        # 4) Query BlueCoat category for the provided hostname
        try:
            credentials = ServerCredentials.from_env(app)
            bc_categories = query_url(credentials, hostname)
        except Exception:
            bc_categories = [FAILED_LOOKUP]

        return RestTestResult(
            input=url,
            normalized_input=hostname,
            matched_url=best_match.url if best_match else "N/A",
            local_categories=[cat.name for cat in matching_cats],
            bc_categories=bc_categories,
        )
