import sqlite3
from typing import Optional, List, Callable

from db.sqlite.util.groups import split_opt_str_group
from db.category import CategoryDBInterface, MutableCategory, Category


def _build_category(row: any) -> Category:
    """Parse SQLite row into a Category object."""
    return Category(
        id=str(row[0]),
        name=row[1],
        description=row[2],
        color=row[3],
        is_deleted=0,
        nested_categories=split_opt_str_group(row[4]),
    )


class SQLiteCategory(CategoryDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            color INTEGER NOT NULL,
                            is_deleted INTEGER DEFAULT 0
        )''')
        self.get_conn().commit()

    def add_category(self, mut_cat: MutableCategory) -> Category:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT INTO categories (name, description, color) VALUES (?, ?, ?)',
            (mut_cat.name, mut_cat.description, mut_cat.color)
        )
        self.get_conn().commit()

        new_cat = Category(
            name = mut_cat.name,
            description = mut_cat.description,
            color = mut_cat.color,
            id = str(cursor.lastrowid),
            is_deleted = 0,
        )
        return new_cat

    def get_category(self, category_id: str) -> Optional[Category]:
        cursor = self.get_conn().cursor()
        cursor.execute(
            '''SELECT
                c.id as id,
                c.name,
                c.description,
                c.color,
                GROUP_CONCAT(sc.child_id) as sub_categories
            FROM categories c
            LEFT JOIN (
                SELECT
                    sc.parent_id,
                    sc.child_id
                FROM sub_category sc
                INNER JOIN categories c
                ON sc.child_id = c.id
                WHERE c.is_deleted = 0 AND sc.is_deleted = 0
            ) sc
            ON c.id = sc.parent_id
            WHERE id = ? AND is_deleted = 0
            GROUP BY c.id''',
            (int(category_id),)
        )
        row = cursor.fetchone()
        if row:
            return _build_category(row)
        return None

    def update_category(self, cat_id: str, category: MutableCategory) -> Category:
        updates = []
        params = []

        # Prepare an update query based on non-None fields
        if category.name is not None:
            updates.append('name = ?')
            params.append(category.name)

        if category.description is not None:
            updates.append('description = ?')
            params.append(category.description)

        if category.color is not None:
            updates.append('color = ?')
            params.append(category.color)

        if updates:
            query = f'UPDATE categories SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(int(cat_id))
            cursor = self.get_conn().cursor()
            cursor.execute(query, params)
            self.get_conn().commit()

        return self.get_category(cat_id)

    def delete_category(self, category_id: str) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'UPDATE categories SET is_deleted = 1 WHERE id = ? AND is_deleted = 0',
            (int(category_id),)
        )
        self.get_conn().commit()

    def get_all_categories(self) -> List[Category]:
        cursor = self.get_conn().cursor()
        cursor.execute(
            '''SELECT
                c.id as id,
                c.name,
                c.description,
                c.color,
                GROUP_CONCAT(sc.child_id) as sub_categories
            FROM categories c
            LEFT JOIN (
                SELECT
                    sc.parent_id,
                    sc.child_id
                FROM sub_category sc
                INNER JOIN categories c
                ON sc.child_id = c.id
                WHERE c.is_deleted = 0 AND sc.is_deleted = 0
            ) sc
            ON c.id = sc.parent_id
            WHERE is_deleted = 0
            GROUP BY c.id'''
        )
        rows = cursor.fetchall()
        return [_build_category(row) for row in rows]
