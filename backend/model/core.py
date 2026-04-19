import uuid
from collections import defaultdict
from datetime import datetime
from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from model.types.category import Category
from model.types.core import Core, Commit
from model.types.mappings import URLCategoryMapping
from model.types.url import URL
from model.util.error import ModelError, CanError
from model.util.parse_localdb import ExistingCat
from routes.types.core import RestCommit
from util.branch_names import BRANCH_PROD


class CoreModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_prod_commit(self) -> RestCommit:
        """Fetch current prod commit"""
        return self.fetch_branch_commit(BRANCH_PROD)

    def fetch_branch_commit(self, branch: str) -> RestCommit:
        """Fetch a commit by branch name"""
        return Commit.read_branch(self.backend, branch).to_rest(self.backend)


    def reset_user_branch(self, user: AuthUser) -> RestCommit:
        """Reset (or Create) a Tag for a specific User"""
        core = Core.read(self.backend)
        prod_commit_hash = core.branches[BRANCH_PROD]
        # create a dummy commit for "pending changes" for the user
        new_commit = Commit(
            uuid=str(uuid.uuid4()),
            author=user.username,
            description=f"Pending changes for \"{user.username}\"",
            created_at=int(datetime.now().timestamp()),
            head=Commit.read(self.backend, prod_commit_hash).head,
            parent_commit_hash=prod_commit_hash,
            ref_changed_uuid=[],
        )
        new_commit.write_branch(self.backend, user.get_branch())
        return new_commit.to_rest(self.backend)

    def check_init(self, user: AuthUser) -> None:
        """Check if we need to initialize a new user"""
        core = Core.read(self.backend)
        if user.get_branch() not in core.branches:
            self.reset_user_branch(user)


    def commit(self, author: AuthUser, description: str) -> CanError[RestCommit]:
        """Commit staged changes to the production Tag"""
        core = Core.read(self.backend)
        prod_commit_hash = core.branches[BRANCH_PROD]

        # fetch current user commit
        user_commit = Commit.read(self.backend, core.branches[author.get_branch()])
        if user_commit.parent_commit_hash != prod_commit_hash:
            return None, ModelError("User Branch is not based on the latest production commit")

        # update for publishing
        user_commit.description = description
        user_commit.created_at = int(datetime.now().timestamp())

        # write new commit to DB
        user_commit.write_branch(self.backend, BRANCH_PROD)

        # reset user branch, to clean up after merge
        # this also clears the uuid so that it does not get reused
        self.reset_user_branch(author)

        return user_commit.to_rest(self.backend), None


    def batch_import(self, branch: str, data: List[ExistingCat]) -> None:
        commit = Commit.read_branch(self.backend, branch)

        # 1. batch insert (new) URLs
        existing_url_name_lut = {url.url: url for url in commit.head.url_lut(self.backend).values()}
        required_urls = set([url for cat in data for url in cat.urls])
        missing_urls = required_urls - set(existing_url_name_lut.keys())
        new_urls = [URL.new(url) for url in missing_urls]
        new_url_hashes = URL.batch_write(self.backend, new_urls)
        for url in new_urls:
            existing_url_name_lut[url.url] = url
        commit.head.urls.extend(new_url_hashes)

        # 2. batch insert (new) Categories
        existing_cat_name_lut = {cat.name: cat for cat in commit.head.category_lut(self.backend).values()}
        required_cats = set([cat.name for cat in data])
        missing_cats = required_cats - set(existing_cat_name_lut.keys())
        new_cats = [Category.new(cat) for cat in missing_cats]
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
