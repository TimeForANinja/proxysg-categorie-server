from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface


class StagingDBURLCategory:
    def __init__(self, db: DBInterface):
        self._db = db

    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        return self._db.url_categories.get_url_categories_by_url(url_id)

    def add_url_category(self, auth: AuthUser, url_id: str, cat_id: str) -> None:
        self._db.url_categories.add_url_category(url_id, cat_id)
        self._db.history.add_history_event(f'Added cat {cat_id} to url {url_id}', auth, [], [url_id], [cat_id])

    def delete_url_category(self, auth: AuthUser, url_id: str, cat_id: str) -> None:
        self._db.url_categories.delete_url_category(url_id, cat_id)
        self._db.history.add_history_event(f'Removed cat {cat_id} from url {url_id}', auth, [], [url_id], [cat_id])

    def set_url_categories(self, auth: AuthUser, url_id: str, cat_ids: List[str]) -> None:
        is_cats = self._db.url_categories.get_url_categories_by_url(url_id)

        added = list(set(cat_ids) - set(is_cats))
        removed = list(set(is_cats) - set(cat_ids))

        for cat in added:
            self._db.url_categories.add_url_category(url_id, cat)
        for cat in removed:
            self._db.url_categories.delete_url_category(url_id, cat)

        self._db.history.add_history_event(
            f'Updated Cats for URL {url_id} from {",".join([str(c) for c in is_cats])} to {",".join([str(c) for c in cat_ids])}',
            auth,
            [],
            [url_id],
            cat_ids,
        )