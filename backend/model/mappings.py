from typing import List, Dict, Optional

from db.abc.db import DBInterface
from model.types.category import Category
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping
from model.types.shared import Constraint
from model.types.token import Token
from model.types.url import URL
from model.types.core import Commit
from routes.types.url import RestConstrainedURL


class MappingModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def get_category_urls(self, branch: str, category_id: str) -> List[RestConstrainedURL]:
        """Fetch all URLs related to a Category"""
        commit = Commit.read_branch(self.backend, branch)

        # Fetch all URL, and build LUT
        url_lut: Dict[str, URL] = {
            u.id: u for u in [
                URL.read(self.backend, url_hash)
                for url_hash in commit.head.urls
            ]
        }

        data: List[RestConstrainedURL] = []
        for map_hash in commit.head.url_category_mappings:
            mapping = URLCategoryMapping.read(self.backend, map_hash)
            if mapping.category_id == category_id:
                data.append(RestConstrainedURL(
                    url=url_lut[mapping.url_id],
                    constraint=mapping.constraint,
                ))

        return data

    def add_url_category(self, branch: str, category_id: str, url_id: str, constraint: Optional[Constraint]) -> None:
        """Add a new url <-> category mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # verify that url and category exist
        url_ids = [URL.read(self.backend, url_hash).id for url_hash in commit.head.urls]
        if url_id not in url_ids:
            raise Exception(f"url with id {url_id} does not exist")

        category_ids = [Category.read(self.backend, cat_hash).id for cat_hash in commit.head.categories]
        if category_id not in category_ids:
            raise Exception(f"category with id {category_id} does not exist")

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

    def delete_url_category(self, branch: str, category_id: str, url_id: str) -> None:
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
            raise Exception("Mapping not found")

        # update commit, removing the mapping
        commit.head.url_category_mappings.remove(found_map)

        # update branch with new commit
        commit.write_branch(self.backend, branch)


    def get_token_categories(self, branch: str, token_id: str) -> List[Category]:
        """Fetch all categories related to a Token"""
        commit = Commit.read_branch(self.backend, branch)

        # Fetch all Category, and build LUT
        category_lut: Dict[str, Category] = {
            c.id: c for c in [
                Category.read(self.backend, cat_hash)
                for cat_hash in commit.head.categories
            ]
        }
        data: List[Category] = []
        for map_hash in commit.head.token_category_mappings:
            mapping = TokenCategoryMapping.read(self.backend, map_hash)
            if mapping.token_id == token_id:
                data.append(category_lut[mapping.category_id])

        return data

    def add_token_category(self, branch: str, token_id: str, category_id: str) -> None:
        """Add a category <-> token mapping"""
        commit = Commit.read_branch(self.backend, branch)

        # verify that token and category exist
        token_ids = [Token.read(self.backend, token_hash).id for token_hash in commit.head.tokens]
        if token_id not in token_ids:
            raise Exception(f"token with id {token_id} does not exist")

        category_ids = [Category.read(self.backend, cat_hash).id for cat_hash in commit.head.categories]
        if category_id not in category_ids:
            raise Exception(f"category with id {category_id} does not exist")

        new_mapping = TokenCategoryMapping(
            token_id=token_id,
            category_id=category_id
        )
        new_map_hash = new_mapping.write(self.backend)

        # update commit with new mapping
        commit.head.token_category_mappings.append(new_map_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)

    def delete_token_category(self, branch: str, token_id: str, category_id: str) -> None:
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
            raise Exception("Mapping not found")

        # update commit, removing the mapping
        commit.head.token_category_mappings.remove(found_map)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
