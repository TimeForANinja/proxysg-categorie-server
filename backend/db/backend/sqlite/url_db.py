import sqlite3
import time
from contextlib import AbstractContextManager
from typing import Optional, List, Any, Callable

from db.backend.abc.url import URLDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.util.groups import split_opt_str_group, join_str_group
from db.backend.sqlite.util.query_builder import build_update_query
from db.dbmodel.url import MutableURL, URL, NO_BC_CATEGORY_YET


def _build_url(row: Any) -> URL:
    """Parse SQLite row into URL object."""
    return URL(
        id=str(row[0]),
        hostname=row[1],
        description=row[2],
        is_deleted=0,
        bc_cats=split_opt_str_group(row[3]),
        bc_last_set=row[4],
        categories=split_opt_str_group(row[5]),
        pending_changes=False,
    )


class SQLiteURL(URLDBInterface):
    def __init__(
            self,
            get_cursor: Callable[[], AbstractContextManager[sqlite3.Cursor]]
        ):
        self.get_cursor = get_cursor

    def add_url(self, mut_url: MutableURL, url_id: str, session: Optional[MyTransactionType] = None) -> URL:
        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT INTO urls (id, hostname, description, bc_cats) VALUES (?, ?, ?, ?)',
                (url_id, mut_url.hostname, mut_url.description, NO_BC_CATEGORY_YET)
            )

        return URL.from_mutable(url_id, mut_url)

    def get_url(self, url_id: str, session: Optional[MyTransactionType] = None) -> Optional[URL]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT
                    u.id AS id,
                    u.hostname,
                    u.description,
                    u.bc_cats,
                    u.bc_last_set,
                    GROUP_CONCAT(uc.category_id) as categories
                FROM urls u
                LEFT JOIN (
                    SELECT
                        uc.url_id,
                        uc.category_id
                    FROM url_categories uc
                    INNER JOIN categories c
                    ON uc.category_id = c.id
                    WHERE c.is_deleted = 0 AND uc.is_deleted = 0
                ) uc
                ON u.id = uc.url_id
                WHERE u.is_deleted = 0 AND u.id = ?
                GROUP BY u.id''',
                (url_id,)
            )
            row = cursor.fetchone()
        if row:
            return _build_url(row)
        return None

    def update_url(self, url_id: str, mut_url: MutableURL, session: Optional[MyTransactionType] = None) -> URL:
        updates, params = build_update_query(mut_url, {
            'hostname': 'hostname',
            'description': 'description',
        })

        if updates:
            query = f'UPDATE urls SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(url_id)
            with self.get_cursor() as cursor:
                cursor.execute(query, params)

        return self.get_url(url_id)

    def set_bc_cats(self, url_id: str, bc_cats: List[str]):
        query = 'UPDATE urls SET bc_cats = ?, bc_last_set = ? WHERE id = ? AND is_deleted = 0'
        with self.get_cursor() as cursor:
            cursor.execute(query, (join_str_group(bc_cats), int(time.time()), url_id))

    def delete_url(self, url_id: str, session: Optional[MyTransactionType] = None):
        with self.get_cursor() as cursor:
            cursor.execute(
                'UPDATE urls SET is_deleted = ? WHERE id = ? AND is_deleted = 0',
                (int(time.time()), url_id,)
            )

    def get_all_urls(self, session: Optional[MyTransactionType] = None) -> List[URL]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT
                    u.id AS id,
                    u.hostname,
                    u.description,
                    u.bc_cats,
                    u.bc_last_set,
                    GROUP_CONCAT(uc.category_id) as categories
                FROM urls u
                LEFT JOIN (
                    SELECT
                        uc.url_id,
                        uc.category_id
                    FROM url_categories uc
                    INNER JOIN categories c
                    ON uc.category_id = c.id
                    WHERE c.is_deleted = 0 AND uc.is_deleted = 0
                ) uc
                ON u.id = uc.url_id
                WHERE u.is_deleted = 0
                GROUP BY u.id''',
            )
            rows = cursor.fetchall()
        return [_build_url(row) for row in rows]
