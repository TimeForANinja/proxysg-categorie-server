from typing import List, Optional

from db.abc.db import DBInterface
from model.types.category import Category
from model.util.error import ModelError
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping, ChildCategoryMapping
from model.types.shared import Constraint
from model.types.core import Commit
from model.util.find import find_in_lists
from routes.types.url import RestConstrainedURL


class MappingModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def get_category_urls(self, branch: str, category_id: str) -> List[RestConstrainedURL]:
        """Fetch all URLs related to a Category"""
        commit = Commit.read_branch(self.backend, branch)

        # Fetch URL LUT
        url_lut = commit.head.url_lut(self.backend)

        mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)
        return [
            RestConstrainedURL(
                url=url_lut[mapping.url_id],
                constraint=mapping.constraint,
            )
            for mapping in mappings
            if mapping.category_id == category_id
        ]

    def add_url_category(self, branch: str, category_id: str, url_id: str, constraint: Optional[Constraint]) -> Optional[ModelError]:
        """Add a new url <-> category mapping"""
        if constraint is not None:
            if constraint.start > constraint.end:
                return ModelError("Constraint start must be before end")

        commit = Commit.read_branch(self.backend, branch)

        # verify that url and category exist
        url_lut = commit.head.url_lut(self.backend)
        if url_id not in url_lut:
            return ModelError(f"url with id {url_id} does not exist")

        category_lut = commit.head.category_lut(self.backend)
        if category_id not in category_lut:
            return ModelError(f"category with id {category_id} does not exist")

        # check if mapping already exists
        mapping, _ = find_in_lists(
            URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings),
            None,
            lambda m: m.url_id == url_id and m.category_id == category_id
        )
        if mapping:
            return ModelError(f"mapping between url {url_id} and category {category_id} already exists")

        # create mapping
        new_map_hash = URLCategoryMapping.batch_write(self.backend, [
            URLCategoryMapping(
                url_id=url_id,
                category_id=category_id,
                constraint=constraint
            )
        ])[0]

        # update commit with new mapping
        commit.head.url_category_mappings.append(new_map_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)
        return None

    def delete_url_category(self, branch: str, category_id: str, url_id: str) -> Optional[ModelError]:
        """Delete a url <-> category mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # find mapping
        _, mapping_hash = find_in_lists(
            URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings),
            commit.head.url_category_mappings,
            lambda m: m.url_id == url_id and m.category_id == category_id
        )
        if not mapping_hash:
            return ModelError("Mapping not found")

        # update commit, removing the mapping
        commit.head.url_category_mappings.remove(mapping_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None


    def get_token_categories(self, branch: str, token_id: str) -> List[Category]:
        """Fetch all categories related to a Token"""
        commit = Commit.read_branch(self.backend, branch)

        # Fetch Category LUT
        category_lut = commit.head.category_lut(self.backend)

        mappings = TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings)
        return [
            category_lut[mapping.category_id]
            for mapping in mappings
            if mapping.token_id == token_id
        ]

    def add_token_category(self, branch: str, token_id: str, category_id: str) -> Optional[ModelError]:
        """Add a category <-> token mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # verify that token and category exist
        token_lut = commit.head.token_lut(self.backend)
        if token_id not in token_lut:
            return ModelError(f"token with id {token_id} does not exist")

        category_lut = commit.head.category_lut(self.backend)
        if category_id not in category_lut:
            return ModelError(f"category with id {category_id} does not exist")

        # check if mapping already exists
        mapping, _ = find_in_lists(
            TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings),
            None,
            lambda m: m.token_id == token_id and m.category_id == category_id
        )
        if mapping:
            return ModelError(f"mapping between token {token_id} and category {category_id} already exists")

        new_map_hash = TokenCategoryMapping.batch_write(self.backend, [
            TokenCategoryMapping(
                token_id=token_id,
                category_id=category_id,
            )
        ])[0]

        # update commit with new mapping
        commit.head.token_category_mappings.append(new_map_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)
        return None

    def delete_token_category(self, branch: str, token_id: str, category_id: str) -> Optional[ModelError]:
        """Remove a category <-> token mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # find mapping
        _, mapping_hash = find_in_lists(
            TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings),
            commit.head.token_category_mappings,
            lambda m: m.token_id == token_id and m.category_id == category_id
        )
        if not mapping_hash:
            return ModelError("Mapping not found")

        # update commit, removing the mapping
        commit.head.token_category_mappings.remove(mapping_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None


    def get_child_categories(self, branch: str, category_id: str) -> List[Category]:
        """Fetch all child categories of a category"""
        commit = Commit.read_branch(self.backend, branch)

        # Fetch Category LUT
        category_lut = commit.head.category_lut(self.backend)

        mappings = ChildCategoryMapping.batch_read(self.backend, commit.head.child_category_mappings)
        return [
            category_lut[mapping.child_category_id]
            for mapping in mappings
            if mapping.category_id == category_id
        ]

    def add_child_category(self, branch: str, category_id: str, child_category_id: str) -> Optional[ModelError]:
        """Add a child category mapping"""
        commit = Commit.read_branch(self.backend, branch)

        category_lut = commit.head.category_lut(self.backend)
        if category_id not in category_lut:
            return ModelError(f"category with id {category_id} does not exist")
        if child_category_id not in category_lut:
            return ModelError(f"category with id {child_category_id} does not exist")

        # check if mapping already exists
        mapping, _ = find_in_lists(
            ChildCategoryMapping.batch_read(self.backend, commit.head.child_category_mappings),
            None,
            lambda m: m.category_id == category_id and m.child_category_id == child_category_id
        )
        if mapping:
            return ModelError(f"mapping between category {category_id} and category {child_category_id} already exists")

        new_map_hash = ChildCategoryMapping.batch_write(self.backend, [
            ChildCategoryMapping(
                category_id=category_id,
                child_category_id=child_category_id,
            )
        ])[0]

        # update commit with new mapping
        commit.head.child_category_mappings.append(new_map_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)
        return None

    def delete_child_category(self, branch: str, category_id: str, child_category_id: str) -> Optional[ModelError]:
        """Remove a category <-> category mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # find mapping
        _, mapping_hash = find_in_lists(
            ChildCategoryMapping.batch_read(self.backend, commit.head.child_category_mappings),
            commit.head.child_category_mappings,
            lambda m: m.category_id == category_id and m.child_category_id == child_category_id
        )
        if not mapping_hash:
            return ModelError("Mapping not found")

        # update commit, removing the mapping
        commit.head.child_category_mappings.remove(mapping_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None
