import sqlite3
import time
from typing import List, Callable

from db.abc.token_category import TokenCategoryDBInterface


class SQLiteTokenCategory(TokenCategoryDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        cursor = self.get_conn().cursor()
        cursor.execute(
            '''SELECT
                tc.category_id
            FROM token_categories tc
            INNER JOIN categories c
            ON tc.category_id = c.id AND c.is_deleted = 0
            WHERE tc.token_id = ? AND tc.is_deleted = 0''',
            (int(token_id),)
        )
        rows = cursor.fetchall()
        return [str(row[0]) for row in rows]

    def add_token_category(self, token_id: str, category_id: str) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT INTO token_categories (token_id, category_id) VALUES (?, ?)',
            (int(token_id), int(category_id),)
        )
        self.get_conn().commit()

    def delete_token_category(self, token_id: str, category_id: str) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'UPDATE token_categories SET is_deleted = ? WHERE token_id = ? AND category_id = ? AND is_deleted = 0',
            (int(time.time()), int(token_id), int(category_id),)
        )
        self.get_conn().commit()
