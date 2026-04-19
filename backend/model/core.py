import uuid
from datetime import datetime
from typing import List, Optional

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from model.types.core import Core, Commit
from model.util.error import ModelError, CanError
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

    def fetch_commits(
            self,
            branch: str,
            filter_uuid: Optional[List[str]],
    ) -> List[RestCommit]:
        """
        Fetch a list of recent Commits by Name

        :param branch: The branch to fetch commits from
        :param filter_uuid: The UUIDs to filter by, or None to ignore this filter
        :return: A (filtered) list of Commits
        """
        commits = []

        # load first / current commit
        core = Core.read(self.backend)
        uut_hash = core.branches[branch]

        # Iterate over all elements in our linked list
        while uut_hash is not None:
            c = Commit.read(self.backend, uut_hash)

            # check our filters (if provided) and add to our list if we match
            if (
                filter_uuid is None
                or
                any(x in c.ref_changed_uuid for x in filter_uuid)
            ):
                commits.append(c.to_rest(self.backend))

            # update our pointer to the next commit
            uut_hash = c.parent_commit_hash

        return commits


    def list_branches(self) -> List[str]:
        """Fetch a list of all Branches"""
        core = Core.read(self.backend)
        return list(core.branches.keys())
