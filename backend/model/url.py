from typing import Optional

from db.abc.db import DBInterface
from model.types.core import Commit
from model.types.mappings import URLCategoryMapping
from model.util.error import ModelError, CanError
from model.types.url import URL
from model.util.find import find_in_lists, find_all_in_lists


class URLModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def create_url(self, branch: str, value: str, description: str) -> URL:
        """Create a new URL"""
        commit = Commit.read_branch(self.backend, branch)

        # create url
        new_url = URL.new(value, description)
        new_url_hash = URL.batch_write(self.backend, [new_url])[0]

        # update commit with new url
        commit.head.urls.append(new_url_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)

        return new_url

    def update_url(
            self,
            branch: str, url_id: str,
            value: Optional[str],
            description: Optional[str],
    ) -> CanError[URL]:
        """Update the value of an existing URL"""
        commit = Commit.read_branch(self.backend, branch)

        url, url_hash = find_in_lists(
            URL.batch_read(self.backend, commit.head.urls),
            commit.head.urls,
            lambda u: u.id == url_id
        )
        if not url:
            return None, ModelError("URL not found")

        # update url
        if value:
            url.url = value
        if description:
            url.description = description
        new_url_hash = url.write(self.backend)

        # update commit with new url
        commit.head.urls.remove(url_hash)
        commit.head.urls.append(new_url_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return url, None

    def delete_url(self, branch: str, url_id: str) -> Optional[ModelError]:
        """Delete a URL by ID"""
        commit = Commit.read_branch(self.backend, branch)

        url, url_hash = find_in_lists(
            URL.batch_read(self.backend, commit.head.urls),
            commit.head.urls,
            lambda u: u.id == url_id
        )
        if not url:
            return ModelError("URL not found")

        # update commit, removing the url
        commit.head.urls.remove(url_hash)
        self._remove_url_related(commit, url_id)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None

    def _remove_url_related(self, commit: Commit, url_id: str) -> None:
        mappings = URLCategoryMapping.batch_read(self.backend, commit.head.url_category_mappings)
        # filter out all hashes that use this token
        _, keep_hashes = find_all_in_lists(
            mappings,
            commit.head.url_category_mappings,
            lambda m: m.url_id != url_id
        )
        commit.head.url_category_mappings = keep_hashes
