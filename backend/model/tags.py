from db.abc.db import DBInterface
from model.types.tags import Commit
from model.util.tag_name import TAG_PRODUCTION, build_user_tag


class TagModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_tag(self, name: str) -> Commit:
        """Fetch a specific Tag by Name"""
        commit_hash = self.backend.fetch_kv(name)
        return self.fetch_commit(commit_hash)

    def fetch_commit(self, hash: str) -> Commit:
        """Fetch a specific Commit by Hash"""
        return Commit.read(self.backend, hash)

    def reset_user_tag(self, author: str) -> Commit:
        """Reset (or Create) a Tag for a specific User"""
        prod_commit_hash = self.backend.fetch_kv(TAG_PRODUCTION)
        # create a dummy commit for "pending changes" for the user
        new_commit = Commit(
            author=author,
            description=f"Pending changes for {author}",
            head=Commit.read(self.backend, prod_commit_hash).head,
            parent_commit_hash=prod_commit_hash,
        )
        new_commit_id = new_commit.write(self.backend)
        # update user tag to point to new commit
        user_tag = build_user_tag(author)
        self.backend.insert_kv(user_tag, new_commit_id)

        return new_commit

    def commit(self, author: str, description: str) -> Commit:
        """Commit staged changes to the production Tag"""
        prod_commit_hash = self.backend.fetch_kv(TAG_PRODUCTION)
        user_tag = build_user_tag(author)
        user_commit_hash = self.backend.fetch_kv(user_tag)

        # fetch current user commit and update for push to production
        user_commit = self.fetch_commit(user_commit_hash)
        if user_commit.parent_commit_hash is not prod_commit_hash:
            raise Exception("User tag is not pointing to the latest commit")
        user_commit.description = description

        new_prod_commit = user_commit.write(self.backend)
        self.backend.insert_kv(TAG_PRODUCTION, new_prod_commit)

        # reset user tag, to clean up after merge
        self.reset_user_tag(author)

        return user_commit
