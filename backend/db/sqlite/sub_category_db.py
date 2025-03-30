import sqlite3

from db.sub_category import SubCategoryDBInterface
from typing import List


class SQLiteSubCategory(SubCategoryDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS sub_category (
                            id INTEGER PRIMARY KEY,
                            parent_id INTEGER,
                            child_id INTEGER,
                            is_deleted INTEGER DEFAULT 0,
                            FOREIGN KEY (parent_id) REFERENCES categories(id),
                            FOREIGN KEY (child_id) REFERENCES categories(id)
        )''')
        self.conn.commit()

    def get_sub_categories_by_id(self, category_id: int) -> List[int]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT
                sc.child_id
            FROM sub_category sc
            INNER JOIN categories c
            ON sc.child_id = c.id AND c.is_deleted = 0
            WHERE sc.parent_id = ? AND sc.is_deleted = 0''',
            (category_id,)
        )
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def add_sub_category(self, category_id: int, sub_category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO sub_category (parent_id, child_id) VALUES (?, ?)',
            (category_id, sub_category_id,)
        )
        self.conn.commit()

    def delete_sub_category(self, category_id: int, sub_category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE sub_category SET is_deleted = 1 WHERE parent_id = ? AND child_id = ? AND is_deleted = 0',
            (category_id, sub_category_id,)
        )
        self.conn.commit()
