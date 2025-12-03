from typing import List, Optional

from db.backend.abc.token_category import TokenCategoryDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.util.cursor_callable import GetCursorProtocol


class SQLiteTokenCategory(TokenCategoryDBInterface):
    def __init__(
        self,
        get_cursor: GetCursorProtocol
    ):
        self.get_cursor = get_cursor

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT
                    tc.category_id
                FROM token_categories tc
                INNER JOIN categories c
                ON tc.category_id = c.id AND c.is_deleted = 0
                WHERE tc.token_id = ? AND tc.is_deleted = 0''',
                (token_id,)
            )
            rows = cursor.fetchall()
            return [str(row[0]) for row in rows]

    def add_token_category(self, token_id: str, category_id: str, session: Optional[MyTransactionType] = None):
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'INSERT INTO token_categories (token_id, category_id) VALUES (?, ?)',
                (token_id, category_id,)
            )

    def delete_token_category(self, token_id: str, category_id: str, del_timestamp: int, session: Optional[MyTransactionType] = None):
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'UPDATE token_categories SET is_deleted = ? WHERE token_id = ? AND category_id = ? AND is_deleted = 0',
                (del_timestamp, token_id, category_id,)
            )
