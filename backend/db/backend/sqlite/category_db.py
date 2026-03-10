from typing import Optional, List, Any

from db.backend.abc.category import CategoryDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.util.cursor_callable import GetCursorProtocol
from db.dbmodel.category import MutableCategory, Category


def _build_category(row: Any) -> Category:
    """Parse SQLite row into a Category object."""
    return Category(
        id=str(row[0]),
        name=row[1],
        description=row[2],
        color=row[3],
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
        session: Optional[MyTransactionType] = None,
    ) -> str:
        import uuid
        category_id = str(uuid.uuid4())
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'INSERT INTO categories (id, name, description, color) VALUES (?, ?, ?, ?)',
                (category_id, mut_cat.name, mut_cat.description, mut_cat.color)
            )

        return category_id

    def get_category(self, category_id: str, session: Optional[MyTransactionType] = None) -> Optional[Category]:
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                '''SELECT
                    id,
                    name,
                    description,
                    color
                FROM categories
                WHERE id = ?''',
                (category_id,)
            )
            row = cursor.fetchone()
        if row:
            return _build_category(row)
        return None

    def get_all_categories(self, session: Optional[MyTransactionType] = None) -> List[Category]:
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                '''SELECT
                    id,
                    name,
                    description,
                    color
                FROM categories'''
            )
            rows = cursor.fetchall()
        return [_build_category(row) for row in rows]
