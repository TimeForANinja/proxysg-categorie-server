from collections import defaultdict
from datetime import datetime
from typing import List, Optional, Union, Tuple

from db.abc.db import DBInterface
from model.types.category import Category
from model.types.core import Core
from model.types.url import URL
from model.util.build_localdb import build_localdb
from model.util.error import ModelError
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping, ChildCategoryMapping
from model.util.parse_localdb import ExistingCat
from model.types.core import Commit
from model.types.metrics import TokenUsage, BCCategory
from util.branch_names import BRANCH_PROD
from model.util.matching import unnest_categories


ERROR_NOT_FOUND = ModelError("Not Found")
ERROR_UNCHANGED = ModelError("Not Changed")


class SpecialModel:
    """Special Read-Only Routes useful for the Frontend"""
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def compile_localdb(self, token_val: str, last_access: Optional[int]) -> Union[
        Tuple[None, Optional[int], ModelError],
        Tuple[str, int, None]
    ]:
        commit = Commit.read_branch(self.backend, BRANCH_PROD)

        # fetch all tokens and search for our token by value
        token_lut = commit.head.token_lut(self.backend)
        token = next((t for t in token_lut.values() if t.token_value == token_val), None)
        if not token:
            return None, None, ERROR_NOT_FOUND

        # update token usage
        TokenUsage.track_access(self.backend, token.id)

        # read data required to build localdb
        categories = commit.head.category_lut(self.backend)
        urls = commit.head.url_lut(self.backend)
        cat_mappings = TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings)
        url_mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)
        child_cat_mappings = ChildCategoryMapping.batch_read(self.backend, commit.head.child_category_mappings)

        # calculate when our state has last changed
        # required to support http status 304 with "Last-Modified" and "If-Modified-Since" Headers
        ## start with the creation date of the last commit
        last_modified = commit.created_at
        time_now = int(datetime.now().timestamp())
        ## then offset if we find a constraint that has triggered since last access
        for m in url_mappings:
            if m.constraint is not None:
                if m.constraint.start > 0 and last_modified < m.constraint.start < time_now:
                    last_modified = m.constraint.start
                if m.constraint.end > 0 and last_modified < m.constraint.end < time_now:
                    last_modified = m.constraint.end

        if last_access is not None and last_modified <= last_access:
            # no changes in our model since last access
            return None, last_modified, ERROR_UNCHANGED

        return build_localdb(
            token, urls, categories,
            cat_mappings, url_mappings, child_cat_mappings,
            last_modified,
        ), last_modified, None


    def batch_import(self, branch: str, data: List[ExistingCat]) -> None:
        commit = Commit.read_branch(self.backend, branch)

        # 1. batch insert (new) URLs
        existing_url_name_lut = {url.url: url for url in commit.head.url_lut(self.backend).values()}
        required_urls = set([url for cat in data for url in cat.urls])
        missing_urls = required_urls - set(existing_url_name_lut.keys())
        new_urls = [URL.new(url, "") for url in missing_urls]
        new_url_hashes = URL.batch_write(self.backend, new_urls)
        for url in new_urls:
            existing_url_name_lut[url.url] = url
        commit.head.urls.extend(new_url_hashes)

        # 2. batch insert (new) Categories
        existing_cat_name_lut = {cat.name: cat for cat in commit.head.category_lut(self.backend).values()}
        required_cats = set([cat.name for cat in data])
        missing_cats = required_cats - set(existing_cat_name_lut.keys())
        new_cats = [Category.new(cat, "") for cat in missing_cats]
        new_cat_hashes = Category.batch_write(self.backend, new_cats)
        for cat in new_cats:
            existing_cat_name_lut[cat.name] = cat
        commit.head.categories.extend(new_cat_hashes)

        # 3. batch insert (new) Mappings
        missing_mappings = set()
        # build a LUT of existing mappings
        existing_mapping_lut = defaultdict(list)
        for mapping in URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings):
            existing_mapping_lut[mapping.category_id].append(mapping.url_id)
        for cat in data:
            # resolve IDs using our LUT
            cat_obj = existing_cat_name_lut[cat.name]
            existing_mappings = set(existing_mapping_lut[cat_obj.id])
            # iterate through urls of the category and add mapping if not already mapped
            for url_value in cat.urls:
                url_obj = existing_url_name_lut[url_value]
                if url_obj.id not in existing_mappings:
                    # since tuples are immutable, they still get deduplicated by the set
                    missing_mappings.add((url_obj.id, cat_obj.id))
        # push new mappings to DB
        new_mapping_hashes = URLCategoryMapping.batch_write(self.backend, [
            URLCategoryMapping(url_id, cat_id, None) for url_id, cat_id in missing_mappings
        ])
        commit.head.url_category_mappings.extend(new_mapping_hashes)

        # update branch with new tree
        commit.write_branch(self.backend, branch)


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
