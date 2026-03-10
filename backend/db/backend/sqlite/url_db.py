from typing import Optional, List, Any

from db.backend.abc.url import URLDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.util.cursor_callable import GetCursorProtocol
from db.backend.sqlite.util.groups import split_opt_str_group, join_str_group
from db.dbmodel.url import MutableURL, URL


def _build_url(row: Any) -> URL:
    """Parse SQLite row into URL object."""
    return URL(
        id=str(row[0]),
        hostname=row[1],
        description=row[2],
        categories=split_opt_str_group(row[5]),
    )


class SQLiteURL(URLDBInterface):
    def __init__(
        self,
        get_cursor: GetCursorProtocol
    ):
        self.get_cursor = get_cursor

    def add_url(self, mut_url: MutableURL, categories: List[str], session: Optional[MyTransactionType] = None) -> str:
        import uuid
        url_id = str(uuid.uuid4())
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                'INSERT INTO urls (id, hostname, description, categories) VALUES (?, ?, ?, ?)',
                (url_id, mut_url.hostname, mut_url.description, join_str_group(categories))
            )

        return url_id

    def get_url(self, url_id: str, session: Optional[MyTransactionType] = None) -> Optional[URL]:
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                '''SELECT
                    id,
                    hostname,
                    description,
                    categories
                FROM urls
                WHERE id = ?''',
                (url_id,)
            )
            row = cursor.fetchone()
        if row:
            return _build_url(row)
        return None

    def get_all_urls(self, session: Optional[MyTransactionType] = None) -> List[URL]:
        with self.get_cursor(session=session) as cursor:
            cursor.execute(
                '''SELECT
                    id,
                    hostname,
                    description,
                    categories
                FROM urls''',
            )
            rows = cursor.fetchall()
        return [_build_url(row) for row in rows]
