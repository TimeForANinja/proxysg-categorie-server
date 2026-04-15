from typing import Optional, Union, Tuple
from uuid import uuid4

from db.abc.db import DBInterface
from model.types.core import Commit
from model.types.mappings import URLCategoryMapping
from model.types.error import ModelError, CanError
from model.types.url import URL


class URLModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend

    def _find_url(self, commit: Commit, url_id: str) -> Union[Tuple[URL, str], Tuple[None, None]]:
        for url_hash in commit.head.urls:
            url = URL.read(self.backend, url_hash)
            if url.id == url_id:
                return url, url_hash
        return None, None

    def create_url(self, branch: str, value: str) -> URL:
        """Create a new URL"""
        commit = Commit.read_branch(self.backend, branch)

        # create url
        new_url = URL(
            id=str(uuid4()),
            url=value,
        )
        new_url_hash = new_url.write(self.backend)

        # update commit with new url
        commit.head.urls.append(new_url_hash)

        # update branch with tree
        commit.write_branch(self.backend, branch)

        return new_url

    def update_url(
            self,
            branch: str, url_id: str,
            value: Optional[str],
    ) -> CanError[URL]:
        """Update the value of an existing URL"""
        commit = Commit.read_branch(self.backend, branch)

        url, url_hash = self._find_url(commit, url_id)
        if not url:
            return None, ModelError("URL not found")

        # update url
        if value:
            url.url = value
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

        url, url_hash = self._find_url(commit, url_id)
        if not url:
            return ModelError("URL not found")

        # update commit, removing the url
        commit.head.urls.remove(url_hash)
        self._remove_url_related(commit, url_id)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None

    def _remove_url_related(self, commit: Commit, url_id: str) -> None:
        # all mappings using this url
        category_mappings_to_remove = []
        for map_hash in commit.head.url_category_mappings:
            mapping = URLCategoryMapping.read(self.backend, map_hash)
            if mapping.url_id == url_id:
                category_mappings_to_remove.append(map_hash)
        for m in category_mappings_to_remove:
            commit.head.url_category_mappings.remove(m)
