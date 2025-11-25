import time
from typing import Optional, List, Any

from db.backend.abc.category import CategoryDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.util.cursor_callable import GetCursorProtocol
from db.backend.sqlite.util.groups import split_opt_str_group
from db.backend.sqlite.util.query_builder import build_update_query
from db.dbmodel.category import MutableCategory, Category


def _build_category(row: Any) -> Category:
    """Parse SQLite row into a Category object."""
    return Category(
        id=str(row[0]),
        name=row[1],
        description=row[2],
        color=row[3],
        is_deleted=0,
        nested_categories=split_opt_str_group(row[4]),
        pending_changes=False,
    )


class SQLiteCategory(CategoryDBInterface):
    def __init__(
        self,
        get_cursor: GetCursorProtocol
    ):
        self.get_cursor = get_cursor

    def add_category(
        self,
        mut_cat: MutableCategory,
        category_id: str,
        session: Optional[MyTransactionType] = None,
    ) -> Category:
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'INSERT INTO categories (id, name, description, color) VALUES (?, ?, ?, ?)',
                (category_id, mut_cat.name, mut_cat.description, mut_cat.color)
            )

        return Category.from_mutable(category_id, mut_cat)

    def get_category(self, category_id: str, session: Optional[MyTransactionType] = None) -> Optional[Category]:
        with self.get_cursor(session=session) as cursor:
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

    def update_category(
        self,
        cat_id: str,
        category: MutableCategory,
        session: Optional[MyTransactionType] = None,
    ) -> Category:
        updates, params = build_update_query(category, {
            'name': 'name',
            'description': 'description',
            'color': 'color',
        })

        if updates:
            query = f'UPDATE categories SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(cat_id)
            with self.get_cursor(session=session) as cursor:
                cursor.execute(query, params)

        return self.get_category(cat_id)

    def delete_category(
        self,
        category_id: str,
        session: Optional[MyTransactionType] = None
    ):
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'UPDATE categories SET is_deleted = ? WHERE id = ? AND is_deleted = 0',
                (int(time.time()), category_id,)
            )

    def get_all_categories(self, session: Optional[MyTransactionType] = None) -> List[Category]:
        with self.get_cursor(session=session) as cursor:
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
