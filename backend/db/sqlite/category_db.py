import sqlite3
import time
from typing import Optional, List, Callable

from db.sqlite.util.groups import split_opt_str_group
from db.abc.category import CategoryDBInterface, MutableCategory, Category
from db.sqlite.util.query_builder import build_update_query


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

    def add_category(self, mut_cat: MutableCategory, category_id: str) -> Category:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT INTO categories (id, name, description, color) VALUES (?, ?, ?, ?)',
            (category_id, mut_cat.name, mut_cat.description, mut_cat.color)
        )
        self.get_conn().commit()

        new_cat = Category(
            name=mut_cat.name,
            description=mut_cat.description,
            color=mut_cat.color,
            id=category_id,
            is_deleted=0,
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
            (category_id,)
        )
        row = cursor.fetchone()
        if row:
            return _build_category(row)
        return None

    def update_category(self, cat_id: str, category: MutableCategory) -> Category:
        updates, params = build_update_query(category, {
            'name': 'name',
            'description': 'description',
            'color': 'color',
        })

        if updates:
            query = f'UPDATE categories SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(cat_id)
            cursor = self.get_conn().cursor()
            cursor.execute(query, params)
            self.get_conn().commit()

        return self.get_category(cat_id)

    def delete_category(self, category_id: str) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'UPDATE categories SET is_deleted = ? WHERE id = ? AND is_deleted = 0',
            (int(time.time()), category_id,)
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
