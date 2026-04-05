from typing import Optional
from uuid import uuid4

from db.abc.db import DBInterface
from model.types.category import Member, Category, Constraint
from model.types.tags import Commit
from model.util.tag_name import build_user_tag


class CategoryModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def add_category(self, author: str, name: str) -> Category:
        """Add a new Category with the given name and members"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)

        commit = Commit.read(self.backend, commit_hash)

        # create category
        new_category = Category(
            id=str(uuid4()),
            name=name,
            members=[],
        )
        new_category_hash = new_category.write(self.backend)

        # add new category to commit
        commit.head.categories.append(new_category_hash)
        new_commit_hash = commit.write(self.backend)

        # update user's tag with new commit
        self.backend.insert_kv(author_tag, new_commit_hash)

        return new_category

    def update_category(
            self,
            author: str, category_id: str,
            name: Optional[str],
    ) -> Category:
        """Update the name and members of an existing Category"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)

        commit = Commit.read(self.backend, commit_hash)
        for category_hash in commit.head.categories:
            category = Category.read(self.backend, category_hash)
            if category.id != category_id:
                continue

            # update category
            if name is not None:
                category.name = name
            new_category_hash = category.write(self.backend)

            # update commit with new category
            commit.head.categories.remove(category_hash)
            commit.head.categories.append(new_category_hash)
            new_commit_hash = commit.write(self.backend)

            # update user's tag with new commit
            self.backend.insert_kv(author_tag, new_commit_hash)

            return category

        raise Exception("Category not found")

    def delete_category(self, author: str, category_id: str):
        """Delete a Category by ID"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)

        commit = Commit.read(self.backend, commit_hash)
        for category_hash in commit.head.categories:
            category = Category.read(self.backend, category_hash)
            if category.id != category_id:
                continue

            # update commit, removing old category
            commit.head.categories.remove(category_hash)
            new_commit_hash = commit.write(self.backend)

            # update user's tag with new commit
            self.backend.insert_kv(author_tag, new_commit_hash)

            return category

        raise Exception("Category not found")
        # TODO: propagate delete to tokens


    def add_member(self, author: str, category_id: str, url: str, constraint: Constraint) -> Member:
        """Add a new Member to a Category with the given URL and constraint"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)

        commit = Commit.read(self.backend, commit_hash)
        for category_hash in commit.head.categories:
            category = Category.read(self.backend, category_hash)
            if category.id != category_id:
                continue

            # create new member
            # TODO: check if member already exists
            new_member = Member(url=url, constraint=constraint)
            new_member_hash = new_member.write(self.backend)

            # update category
            category.members.append(new_member_hash)
            new_category_hash = category.write(self.backend)

            # update commit with new category
            commit.head.categories.remove(category_hash)
            commit.head.categories.append(new_category_hash)
            new_commit_hash = commit.write(self.backend)

            # update user's tag with new commit
            self.backend.insert_kv(author_tag, new_commit_hash)

            return new_member

        raise Exception("Category not found")

    def delete_member(self, author: str, category_id: str, url: str):
        """Delete a Member from a Category by ID"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)

        commit = Commit.read(self.backend, commit_hash)
        for category_hash in commit.head.categories:
            category = Category.read(self.backend, category_hash)
            if category.id != category_id:
                continue

            for member_hash in category.members:
                member = Member.read(self.backend, member_hash)
                if member.url != url:
                    continue

                # update category, removing the member
                category.members.remove(member_hash)
                new_category_hash = category.write(self.backend)

                # update commit with new category
                commit.head.categories.remove(category_hash)
                commit.head.categories.append(new_category_hash)
                new_commit_hash = commit.write(self.backend)

                # update user's tag with new commit
                self.backend.insert_kv(author_tag, new_commit_hash)

                return
            raise Exception("Member not found in Category")
        raise Exception("Category not found")
