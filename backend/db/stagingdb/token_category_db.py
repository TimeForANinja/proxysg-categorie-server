from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface


class StagingDBTokenCategory:
    def __init__(self, db: DBInterface):
        self._db = db

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        return self._db.token_categories.get_token_categories_by_token(token_id)

    def add_token_category(self, auth: AuthUser, token_id: str, cat_id: str) -> None:
        self._db.token_categories.add_token_category(token_id, cat_id)
        self._db.history.add_history_event(f'Added cat {cat_id} to token {token_id}', auth, [token_id], [], [cat_id])

    def delete_token_category(self, auth: AuthUser, token_id: str, cat_id: str) -> None:
        self._db.token_categories.delete_token_category(token_id, cat_id)
        self._db.history.add_history_event(f'Removed cat {cat_id} from token {token_id}', auth, [token_id], [], [cat_id])

    def set_token_categories(self, auth: AuthUser, token_id: str, cat_ids: List[str]) -> None:
        is_cats = self._db.token_categories.get_token_categories_by_token(token_id)

        added = list(set(cat_ids) - set(is_cats))
        removed = list(set(is_cats) - set(cat_ids))

        for cat in added:
            self._db.token_categories.add_token_category(token_id, cat)
        for cat in removed:
            self._db.token_categories.delete_token_category(token_id, cat)

        self._db.history.add_history_event(
            f'Updated Cats for Token {token_id} from {",".join([str(c) for c in is_cats])} to {",".join([str(c) for c in cat_ids])}',
            auth,
            [token_id],
            [],
            cat_ids,
        )
