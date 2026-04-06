from db.abc.db import DBInterface
from model.types.core import Core, BRANCH_PROD, user_branch_name
from model.types.tags import Commit


class TagModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_prod_commit(self) -> Commit:
        """Fetch a specific Tag by Name"""
        core = Core.read(self.backend)
        return self.fetch_commit(core.branches[BRANCH_PROD])

    def fetch_user_commit(self, author: str) -> Commit:
        """Fetch the latest user commit"""
        core = Core.read(self.backend)
        branch_name = user_branch_name(author)
        return self.fetch_commit(core.branches[branch_name])

    def fetch_commit(self, hash: str) -> Commit:
        """Fetch a specific Commit by Hash"""
        return Commit.read(self.backend, hash)


    def reset_user_branch(self, author: str) -> Commit:
        """Reset (or Create) a Tag for a specific User"""
        core = Core.read(self.backend)
        prod_commit_hash = core.branches[BRANCH_PROD]
        # create a dummy commit for "pending changes" for the user
        new_commit = Commit(
            author=author,
            description=f"Pending changes for {author}",
            head=self.fetch_commit(prod_commit_hash).head,
            parent_commit_hash=prod_commit_hash,
        )
        new_commit.write_branch(self.backend, user_branch_name(author))
        return new_commit


    def commit(self, author: str, description: str) -> Commit:
        """Commit staged changes to the production Tag"""
        core = Core.read(self.backend)
        prod_commit_hash = core.branches[BRANCH_PROD]
        # fetch current user commit and update for push to production
        user_commit = self.fetch_user_commit(author)
        if user_commit.parent_commit_hash is not prod_commit_hash:
            raise Exception("User Branch is not based on the latest production commit")
        user_commit.description = description

        # write new commit to DB
        user_commit.write_branch(self.backend, BRANCH_PROD)

        # reset user tag, to clean up after merge
        self.reset_user_branch(author)

        return user_commit
