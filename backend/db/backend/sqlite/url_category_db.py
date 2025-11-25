import time
from typing import List, Optional

from db.backend.abc.url_category import UrlCategoryDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.util.cursor_callable import GetCursorProtocol


class SQLiteURLCategory(UrlCategoryDBInterface):
    def __init__(
        self,
        get_cursor: GetCursorProtocol
    ):
        self.get_cursor = get_cursor

    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT
                    uc.category_id
                FROM url_categories uc
                INNER JOIN categories c
                ON uc.category_id = c.id AND c.is_deleted = 0
                WHERE uc.url_id = ? AND uc.is_deleted = 0''',
                (url_id,)
            )
            rows = cursor.fetchall()
            return [str(row[0]) for row in rows]

    def add_url_category(self, url_id: str, category_id: str, session: Optional[MyTransactionType] = None):
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'INSERT INTO url_categories (url_id, category_id) VALUES (?, ?)',
                (url_id, category_id,)
            )

    def delete_url_category(self, url_id: str, category_id: str, session: Optional[MyTransactionType] = None):
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'UPDATE url_categories SET is_deleted = ? WHERE url_id = ? AND category_id = ? AND is_deleted = 0',
                (int(time.time()), url_id, category_id,)
            )
