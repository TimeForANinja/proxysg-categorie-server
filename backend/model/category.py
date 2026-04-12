from typing import Optional, Union, Tuple
from uuid import uuid4

from db.abc.db import DBInterface
from model.types.category import Category
from model.types.core import Commit
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping


class CategoryModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend

    def _find_category(self, commit: Commit, cat_id: str) -> Union[Tuple[Category, str], Tuple[None, None]]:
        for category_hash in commit.head.categories:
            category = Category.read(self.backend, category_hash)
            if category.id == cat_id:
                return category, category_hash
        return None, None

    def create_category(self, branch: str, name: str) -> Category:
        """Add a new Category with the given name"""
        commit = Commit.read_branch(self.backend, branch)

        # create category
        new_category = Category(
            id=str(uuid4()),
            name=name,
        )
        new_category_hash = new_category.write(self.backend)

        # update commit with new category
        commit.head.categories.append(new_category_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)

        return new_category

    def update_category(
            self,
            branch: str, category_id: str,
            name: Optional[str],
    ) -> Category:
        """Update the name of an existing Category"""
        commit = Commit.read_branch(self.backend, branch)

        cat, cat_hash = self._find_category(commit, category_id)
        if not cat:
            raise Exception("Category not found")

        # update category
        if name:
            cat.name = name
        new_category_hash = cat.write(self.backend)

        # update commit with new category
        commit.head.categories.remove(cat_hash)
        commit.head.categories.append(new_category_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return cat

    def delete_category(self, branch: str, category_id: str) -> None:
        """Delete a Category by ID"""
        commit = Commit.read_branch(self.backend, branch)

        cat, cat_hash = self._find_category(commit, category_id)
        if not cat:
            raise Exception("Category not found")

        # update commit, removing the category
        commit.head.categories.remove(cat_hash)
        self._remove_category_related(commit, category_id)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

    def _remove_category_related(self, commit: Commit, category_id: str) -> None:
        # all mappings using this category
        url_mappings_to_remove = []
        for map_hash in commit.head.url_category_mappings:
            mapping = URLCategoryMapping.read(self.backend, map_hash)
            if mapping.category_id == category_id:
                url_mappings_to_remove.append(map_hash)
        for m in url_mappings_to_remove:
            commit.head.url_category_mappings.remove(m)

        token_mappings_to_remove = []
        for map_hash in commit.head.token_category_mappings:
            mapping = TokenCategoryMapping.read(self.backend, map_hash)
            if mapping.category_id == category_id:
                token_mappings_to_remove.append(map_hash)
        for m in token_mappings_to_remove:
            commit.head.token_category_mappings.remove(m)
