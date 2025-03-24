import sqlite3
from db.token_category import TokenCategoryDBInterface
from typing import List



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

    def get_token_categories_by_token(self, token_id: int) -> List[int]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT category_id FROM token_categories WHERE token_id = ? AND is_deleted = 0',
            (token_id,)
        )
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def add_token_category(self, token_id: int, category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO token_categories (token_id, category_id) VALUES (?, ?)',
            (token_id, category_id,)
        )
        self.conn.commit()

    def delete_token_category(self, token_id: int, category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE token_categories SET is_deleted = 1 WHERE token_id = ? AND category_id = ? AND is_deleted = 0',
            (token_id, category_id,)
        )
        self.conn.commit()
