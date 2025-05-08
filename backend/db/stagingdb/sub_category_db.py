from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface


class StagingDBSubCategory:
    def __init__(self, db: DBInterface):
        self._db = db

    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        return self._db.sub_categories.get_sub_categories_by_id(category_id)

    def add_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str) -> None:
        self._db.sub_categories.add_sub_category(cat_id, sub_cat_id)
        self._db.history.add_history_event(f'Added sub-cat {sub_cat_id} to cat {cat_id}', auth, [], [], [cat_id, sub_cat_id])

    def delete_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str) -> None:
        self._db.sub_categories.delete_sub_category(cat_id, sub_cat_id)
        self._db.history.add_history_event(f'Removed sub-cat {sub_cat_id} from category {cat_id}', auth, [], [], [cat_id, sub_cat_id])

    def set_sub_categories(self, auth: AuthUser, cat_id: str, cat_ids: List[str]) -> None:
        is_sub_cats = self._db.sub_categories.get_sub_categories_by_id(cat_id)

        added = list(set(cat_ids) - set(is_sub_cats))
        removed = list(set(is_sub_cats) - set(cat_ids))

        for cat in added:
            self._db.sub_categories.add_sub_category(cat_id, cat)
        for cat in removed:
            self._db.sub_categories.delete_sub_category(cat_id, cat)

        self._db.history.add_history_event(
            f'Updated Sub-Cats for Category {cat_id} from {",".join([str(c) for c in is_sub_cats])} to {",".join([str(c) for c in cat_ids])}',
            auth,
            [],
            [],
            [cat_id] + cat_ids,
        )
