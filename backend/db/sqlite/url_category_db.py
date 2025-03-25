import sqlite3
from db.url_category import UrlCategoryDBInterface
from typing import List



class SQLiteURLCategory(UrlCategoryDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS url_categories (
                            id INTEGER PRIMARY KEY,
                            url_id INTEGER,
                            category_id INTEGER,
                            is_deleted INTEGER DEFAULT 0,
                            FOREIGN KEY (url_id) REFERENCES urls(id),
                            FOREIGN KEY (category_id) REFERENCES categories(id)
        )''')
        self.conn.commit()

    def get_url_categories_by_url(self, url_id: int) -> List[int]:
        cursor = self.conn.cursor()
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
        return [row[0] for row in rows]

    def add_url_category(self, url_id: int, category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO url_categories (url_id, category_id) VALUES (?, ?)',
            (url_id, category_id,)
        )
        self.conn.commit()

    def delete_url_category(self, url_id: int, category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE url_categories SET is_deleted = 1 WHERE url_id = ? AND category_id = ? AND is_deleted = 0',
            (url_id, category_id,)
        )
        self.conn.commit()
