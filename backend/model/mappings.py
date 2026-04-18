from typing import List, Optional

from db.abc.db import DBInterface
from model.types.category import Category
from model.util.error import ModelError
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping
from model.types.shared import Constraint
from model.types.core import Commit
from routes.types.url import RestConstrainedURL


class MappingModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def get_category_urls(self, branch: str, category_id: str) -> List[RestConstrainedURL]:
        """Fetch all URLs related to a Category"""
        commit = Commit.read_branch(self.backend, branch)

        # Fetch URL LUT
        url_lut = commit.head.url_lut(self.backend)

        data: List[RestConstrainedURL] = []
        for map_hash in commit.head.url_category_mappings:
            mapping = URLCategoryMapping.read(self.backend, map_hash)
            if mapping.category_id == category_id:
                data.append(RestConstrainedURL(
                    url=url_lut[mapping.url_id],
                    constraint=mapping.constraint,
                ))

        return data

    def add_url_category(self, branch: str, category_id: str, url_id: str, constraint: Optional[Constraint]) -> Optional[ModelError]:
        """Add a new url <-> category mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # verify that url and category exist
        url_lut = commit.head.url_lut(self.backend)
        if url_id not in url_lut:
            return ModelError(f"url with id {url_id} does not exist")

        category_lut = commit.head.category_lut(self.backend)
        if category_id not in category_lut:
            return ModelError(f"category with id {category_id} does not exist")

        # check if mapping already exists
        for map_hash in commit.head.url_category_mappings:
            mapping = URLCategoryMapping.read(self.backend, map_hash)
            if mapping.url_id == url_id and mapping.category_id == category_id:
                return ModelError(f"mapping between url {url_id} and category {category_id} already exists")

        # create mapping
        new_mapping = URLCategoryMapping(
            url_id=url_id,
            category_id=category_id,
            constraint=constraint
        )
        new_map_hash = new_mapping.write(self.backend)

        # update commit with new mapping
        commit.head.url_category_mappings.append(new_map_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)
        return None

    def delete_url_category(self, branch: str, category_id: str, url_id: str) -> Optional[ModelError]:
        """Delete a url <-> category mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # find mapping
        found_map: Optional[str] = None
        for map_hash in commit.head.url_category_mappings:
            mapping = URLCategoryMapping.read(self.backend, map_hash)
            if mapping.url_id == url_id and mapping.category_id == category_id:
                found_map = map_hash
                break

        if not found_map:
            return ModelError("Mapping not found")

        # update commit, removing the mapping
        commit.head.url_category_mappings.remove(found_map)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None


    def get_token_categories(self, branch: str, token_id: str) -> List[Category]:
        """Fetch all categories related to a Token"""
        commit = Commit.read_branch(self.backend, branch)

        # Fetch Category LUT
        category_lut = commit.head.category_lut(self.backend)

        data: List[Category] = []
        for map_hash in commit.head.token_category_mappings:
            mapping = TokenCategoryMapping.read(self.backend, map_hash)
            if mapping.token_id == token_id:
                data.append(category_lut[mapping.category_id])

        return data

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
        for map_hash in commit.head.token_category_mappings:
            mapping = TokenCategoryMapping.read(self.backend, map_hash)
            if mapping.token_id == token_id and mapping.category_id == category_id:
                return ModelError(f"mapping between token {token_id} and category {category_id} already exists")

        new_mapping = TokenCategoryMapping(
            token_id=token_id,
            category_id=category_id
        )
        new_map_hash = new_mapping.write(self.backend)

        # update commit with new mapping
        commit.head.token_category_mappings.append(new_map_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)
        return None

    def delete_token_category(self, branch: str, token_id: str, category_id: str) -> Optional[ModelError]:
        """Remove a category <-> token mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # find mapping
        found_map: Optional[str] = None
        for map_hash in commit.head.token_category_mappings:
            mapping = TokenCategoryMapping.read(self.backend, map_hash)
            if mapping.token_id == token_id and mapping.category_id == category_id:
                found_map = map_hash
                break

        if not found_map:
            return ModelError("Mapping not found")

        # update commit, removing the mapping
        commit.head.token_category_mappings.remove(found_map)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None
