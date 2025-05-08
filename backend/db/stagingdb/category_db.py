from typing import Optional, List

from auth.auth_user import AuthUser
from db.abc.category import MutableCategory, Category
from db.abc.db import DBInterface


class StagingDBCategory:
    def __init__(self, db: DBInterface):
        self._db = db

    def add_category(self, auth: AuthUser, category: MutableCategory) -> Category:
        new_category = self._db.categories.add_category(category)
        self._db.history.add_history_event(f'Category {new_category.id} created', auth, [], [], [new_category.id])
        return new_category

    def get_category(self, category_id: str) -> Optional[Category]:
        return self._db.categories.get_category(category_id)

    def update_category(self, auth: AuthUser, cat_id: str, category: MutableCategory) -> Category:
        new_cat = self._db.categories.update_category(cat_id, category)
        self._db.history.add_history_event(f'Category {cat_id} updated', auth, [], [], [cat_id])
        return new_cat

    def delete_category(self, auth: AuthUser, cat_id: str) -> None:
        self._db.categories.delete_category(cat_id)
        self._db.history.add_history_event(f'Category {cat_id} deleted', auth, [], [], [cat_id])

    def get_all_categories(self) -> List[Category]:
        return self._db.categories.get_all_categories()
