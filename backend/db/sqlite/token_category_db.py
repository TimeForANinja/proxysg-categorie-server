import sqlite3
from typing import List

from db.token_category import TokenCategoryDBInterface


class SQLiteTokenCategory(TokenCategoryDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS token_categories (
                            id INTEGER PRIMARY KEY,
                            token_id INTEGER,
                            category_id INTEGER,
                            is_deleted INTEGER DEFAULT 0,
                            FOREIGN KEY (token_id) REFERENCES tokens(id),
                            FOREIGN KEY (category_id) REFERENCES categories(id)
        )''')
        self.conn.commit()

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        cursor = self.conn.cursor()
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
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO token_categories (token_id, category_id) VALUES (?, ?)',
            (int(token_id), int(category_id),)
        )
        self.conn.commit()

    def delete_token_category(self, token_id: str, category_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE token_categories SET is_deleted = 1 WHERE token_id = ? AND category_id = ? AND is_deleted = 0',
            (int(token_id), int(category_id),)
        )
        self.conn.commit()
