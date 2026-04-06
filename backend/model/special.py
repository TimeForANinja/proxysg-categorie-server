from collections import defaultdict
from dataclasses import dataclass
from typing import List

from db.abc.db import DBInterface
from model.types.category import Category, Member
from model.types.core import Core
from model.types.tags import Commit


@dataclass
class URLMapping:
    url: str
    categories: List[str]


class SpecialModel:
    """Special Read-Only Routes useful for the Rest-API"""
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_url_list(self, branch: str) -> List[URLMapping]:
        """Fetch a list of all URLs"""
        head_commit = Commit.read_branch(self.backend, branch)
        urls = defaultdict(list)

        for cat_hash in head_commit.head.categories:
            cat = Category.read(self.backend, cat_hash)
            for member_hash in cat.members:
                member = Member.read(self.backend, member_hash)
                urls[member.url].append(cat.name)

        # typecast
        return [
            URLMapping(url=url, categories=categories)
            for url, categories in urls.items()
        ]

    def fetch_commits(self, branch: str) -> List[Commit]:
        """Fetch a list of recent Commits by Name"""
        head_commit = Commit.read_branch(self.backend, branch)
        commits = []

        # Iterate over all elements in our linked list
        lut = head_commit.parent_commit_hash
        while lut is not None:
            c = Commit.read(self.backend, lut)
            commits.append(c)
            lut = c.parent_commit_hash

        return commits

    def list_branches(self) -> List[str]:
        """Fetch a list of all Branches"""
        core = Core.read(self.backend)
        return list(core.branches.keys())
