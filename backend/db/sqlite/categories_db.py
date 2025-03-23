import sqlite3
from db.categories import CategoriesDBInterface, MutableCategory, Category
from typing import Optional, List


class SQLCategories(CategoriesDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            color INTEGER NOT NULL,
                            is_deleted INTEGER DEFAULT 0
        )''')
        self.conn.commit()

    def add_category(self, mut_cat: MutableCategory) -> Category:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO categories (name, description, color) VALUES (?, ?, ?)',
            (mut_cat.name, mut_cat.description, mut_cat.color)
        )
        self.conn.commit()

        cat = Category(
            name = mut_cat.name,
            description = mut_cat.description,
            color = mut_cat.color,
            id = cursor.lastrowid,
            is_deleted = 0,
        )
        return cat

    def get_category(self, category_id: int) -> Optional[Category]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, name, description, color, is_deleted FROM categories WHERE id = ? AND is_deleted = 0',
            (category_id,)
        )
        row = cursor.fetchone()
        if row:
            return Category(
                id=row[0],
                name=row[1],
                description=row[2],
                color=row[3],
                is_deleted=row[4],
            )
        return None

    def update_category(self, cat_id: int, category: MutableCategory) -> Category:
        updates = []
        params = []

        # Prepare update query based on non-None fields
        if category.name is not None:
            updates.append("name = ?")
            params.append(category.name)

        if category.description is not None:
            updates.append("description = ?")
            params.append(category.description)

        if category.color is not None:
            updates.append("color = ?")
            params.append(category.color)

        if updates:
            query = f'UPDATE categories SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(cat_id)
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()

        return self.get_category(cat_id)

    def delete_category(self, category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE categories SET is_deleted = 1 WHERE id = ? AND is_deleted = 0',
            (category_id,)
        )
        self.conn.commit()

    def get_all_categories(self) -> List[Category]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, name, color, description, is_deleted FROM categories WHERE is_deleted = 0'
        )
        rows = cursor.fetchall()
        return [Category(
            id=row[0],
            name=row[1],
            color=row[2],
            description=row[3],
            is_deleted=row[4],
        ) for row in rows]
