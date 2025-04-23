import sqlite3
from typing import List, Callable

from db.url_category import UrlCategoryDBInterface


class SQLiteURLCategory(UrlCategoryDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        cursor = self.get_conn().cursor()
        cursor.execute(
            '''SELECT
                uc.category_id
            FROM url_categories uc
            INNER JOIN categories c
            ON uc.category_id = c.id AND c.is_deleted = 0
            WHERE uc.url_id = ? AND uc.is_deleted = 0''',
            (int(url_id),)
        )
        rows = cursor.fetchall()
        return [str(row[0]) for row in rows]

    def add_url_category(self, url_id: str, category_id: str) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT INTO url_categories (url_id, category_id) VALUES (?, ?)',
            (int(url_id), int(category_id),)
        )
        self.get_conn().commit()

    def delete_url_category(self, url_id: str, category_id: str) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'UPDATE url_categories SET is_deleted = 1 WHERE url_id = ? AND category_id = ? AND is_deleted = 0',
            (int(url_id), int(category_id),)
        )
        self.get_conn().commit()
