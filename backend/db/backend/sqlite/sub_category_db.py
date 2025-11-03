import sqlite3
import time
from contextlib import AbstractContextManager
from typing import List, Callable

from db.backend.abc.sub_category import SubCategoryDBInterface
from db.backend.abc.util.types import MyTransactionType


class SQLiteSubCategory(SubCategoryDBInterface):
    def __init__(
            self,
            get_cursor: Callable[[], AbstractContextManager[sqlite3.Cursor]]
        ):
        self.get_cursor = get_cursor

    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT
                    sc.child_id
                FROM sub_category sc
                INNER JOIN categories c
                ON sc.child_id = c.id AND c.is_deleted = 0
                WHERE sc.parent_id = ? AND sc.is_deleted = 0''',
                (int(category_id),)
            )
            rows = cursor.fetchall()
        return [str(row[0]) for row in rows]

    def add_sub_category(self, category_id: str, sub_category_id: str, session: MyTransactionType = None) -> None:
        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT INTO sub_category (parent_id, child_id) VALUES (?, ?)',
                (int(category_id), int(sub_category_id),)
            )

    def delete_sub_category(self, category_id: str, sub_category_id: str, session: MyTransactionType = None) -> None:
        with self.get_cursor() as cursor:
            cursor.execute(
                'UPDATE sub_category SET is_deleted = ? WHERE parent_id = ? AND child_id = ? AND is_deleted = 0',
                (int(time.time()), int(category_id), int(sub_category_id),)
            )
