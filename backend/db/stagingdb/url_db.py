from typing import Optional, List
import uuid

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.url import MutableURL, URL


class StagingDBURL:
    def __init__(self, db: DBInterface):
        self._db = db

    def add_url(self, auth: AuthUser, mut_url: MutableURL) -> URL:
        url_id = str(uuid.uuid4())
        new_url = self._db.urls.add_url(mut_url, url_id)
        self._db.history.add_history_event(f'URL {new_url.id} created', auth, [], [new_url.id], [])
        return new_url

    def get_url(self, url_id: str) -> Optional[URL]:
        return self._db.urls.get_url(url_id)

    def update_url(self, auth: AuthUser, url_id: str, mut_url: MutableURL) -> URL:
        new_url = self._db.urls.update_url(url_id, mut_url)
        self._db.history.add_history_event(f'URL {url_id} updated', auth, [], [url_id], [])
        return new_url

    def set_bc_cats(self, url_id: str, bc_cats: List[str]) -> None:
        return self._db.urls.set_bc_cats(url_id, bc_cats)

    def delete_url(self, auth: AuthUser, url_id: str) -> None:
        self._db.urls.delete_url(url_id)
        self._db.history.add_history_event(f'URL {url_id} deleted', auth, [], [url_id], [])

    def get_all_urls(self) -> List[URL]:
        return self._db.urls.get_all_urls()
