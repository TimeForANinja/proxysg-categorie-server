from typing import Optional

from db.abc.db import DBInterface
from model.types.category import Category
from model.types.core import Commit
from model.util.error import CanError, ModelError
from model.types.mappings import URLCategoryMapping, TokenCategoryMapping
from model.util.find import find_in_lists, find_all_in_lists


class CategoryModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def create_category(self, branch: str, name: str) -> Category:
        """Add a new Category with the given name"""
        commit = Commit.read_branch(self.backend, branch)

        # create category
        new_category = Category.new(name)
        new_category_hash = Category.batch_write(self.backend, [new_category])[0]

        # update commit with new category
        commit.head.categories.append(new_category_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)

        return new_category

    def update_category(
            self,
            branch: str, category_id: str,
            name: Optional[str],
    ) -> CanError[Category]:
        """Update the name of an existing Category"""
        commit = Commit.read_branch(self.backend, branch)

        cat, cat_hash = find_in_lists(
            Category.batch_read(self.backend, commit.head.categories),
            commit.head.categories,
            lambda u: u.id == category_id
        )
        if not cat:
            return None, ModelError("Category not found")

        # update category
        if name:
            cat.name = name
        new_category_hash = cat.write(self.backend)

        # update commit with new category
        commit.head.categories.remove(cat_hash)
        commit.head.categories.append(new_category_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return cat, None

    def delete_category(self, branch: str, category_id: str) -> Optional[ModelError]:
        """Delete a Category by ID"""
        commit = Commit.read_branch(self.backend, branch)

        cat, cat_hash = find_in_lists(
            Category.batch_read(self.backend, commit.head.categories),
            commit.head.categories,
            lambda u: u.id == category_id
        )
        if not cat:
            return ModelError("Category not found")

        # update commit, removing the category
        commit.head.categories.remove(cat_hash)
        self._remove_category_related(commit, category_id)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None

    def _remove_category_related(self, commit: Commit, category_id: str) -> None:
        url_mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)
        token_mappings = TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings)
        # filter out all hashes that use this token

        _, keep_url_hashes = find_all_in_lists(
            url_mappings,
            commit.head.url_category_mappings,
            lambda m: m.category_id != category_id
        )
        commit.head.url_category_mappings = keep_url_hashes

        _, keep_token_hashes = find_all_in_lists(
            token_mappings,
            commit.head.token_category_mappings,
            lambda m: m.category_id != category_id
        )
        commit.head.token_category_mappings = keep_token_hashes
