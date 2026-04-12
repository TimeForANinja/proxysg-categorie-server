import uuid
from datetime import datetime

from db.abc.db import DBInterface
from model.types.core import Core, Commit
from routes.types.core import RestCommit
from util.branch_names import BRANCH_PROD, user_branch_name


class CoreModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_prod_commit(self) -> RestCommit:
        """Fetch current prod commit"""
        return self.fetch_branch_commit(BRANCH_PROD)

    def fetch_user_commit(self, author: str) -> RestCommit:
        """Fetch a user commit"""
        return self.fetch_branch_commit(user_branch_name(author))

    def fetch_branch_commit(self, branch: str) -> RestCommit:
        """Fetch a commit by branch name"""
        return Commit.read_branch(self.backend, branch).to_rest(self.backend)


    def reset_user_branch(self, user: str) -> RestCommit:
        """Reset (or Create) a Tag for a specific User"""
        core = Core.read(self.backend)
        prod_commit_hash = core.branches[BRANCH_PROD]
        # create a dummy commit for "pending changes" for the user
        new_commit = Commit(
            uuid=str(uuid.uuid4()),
            author=user,
            description=f"Pending changes for {user}",
            created_at=int(datetime.now().timestamp()),
            head=Commit.read(self.backend, prod_commit_hash).head,
            parent_commit_hash=prod_commit_hash,
        )
        new_commit.write_branch(self.backend, user_branch_name(user))
        return new_commit.to_rest(self.backend)


    def commit(self, author: str, description: str) -> Commit:
        """Commit staged changes to the production Tag"""
        core = Core.read(self.backend)
        prod_commit_hash = core.branches[BRANCH_PROD]

        # fetch current user commit
        user_commit = Commit.read(self.backend, user_branch_name(author))
        if user_commit.parent_commit_hash != prod_commit_hash:
            raise Exception("User Branch is not based on the latest production commit")

        # update for publishing
        user_commit.description = description
        user_commit.created_at = int(datetime.now().timestamp())

        # write new commit to DB
        user_commit.write_branch(self.backend, BRANCH_PROD)

        # reset user branch, to clean up after merge
        # this also clears the uuid, so that it does not get reused
        self.reset_user_branch(author)

        return user_commit
