import sqlite3
import time
from typing import Optional, List, Callable

from db.sqlite.util.groups import split_opt_str_group
from db.abc.url import MutableURL, URL, NO_BC_CATEGORY_YET, URLDBInterface


def _build_url(row: any) -> URL:
    """Parse SQLite row into URL object."""
    return URL(
        id=str(row[0]),
        hostname=row[1],
        description=row[2],
        is_deleted=0,
        bc_cats=split_opt_str_group(row[3]),
        categories=split_opt_str_group(row[4]),
    )


class SQLiteURL(URLDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def add_url(self, mut_url: MutableURL) -> URL:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT INTO urls (hostname, description, bc_cats) VALUES (?, ?, ?)',
            (mut_url.hostname,mut_url.description, NO_BC_CATEGORY_YET)
        )
        self.get_conn().commit()

        new_url = URL(
            hostname=mut_url.hostname,
            description=mut_url.description,
            id=str(cursor.lastrowid),
            is_deleted=0,
            bc_cats=[NO_BC_CATEGORY_YET],
        )
        return new_url

    def get_url(self, url_id: str) -> Optional[URL]:
        cursor = self.get_conn().cursor()
        cursor.execute(
            '''SELECT
                u.id AS id,
                u.hostname,
                u.description,
                u.bc_cats,
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
            (int(url_id),)
        )
        row = cursor.fetchone()
        if row:
            return _build_url(row)
        return None

    def update_url(self, url_id: str, mut_url: MutableURL) -> URL:
        updates = []
        params = []

        # Prepare an update query based on non-None fields
        if mut_url.hostname is not None:
            updates.append('hostname = ?')
            params.append(mut_url.hostname)
        if mut_url.description is not None:
            updates.append('description = ?')
            params.append(mut_url.description)

        if updates:
            query = f'UPDATE urls SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(int(url_id))
            cursor = self.get_conn().cursor()
            cursor.execute(query, params)
            self.get_conn().commit()

        return self.get_url(url_id)

    def set_bc_cats(self, url_id: str, bc_cats: List[str]) -> None:
        query = 'UPDATE urls SET bc_cats = ? WHERE id = ? AND is_deleted = 0'
        cursor = self.get_conn().cursor()
        cursor.execute(query, (','.join(bc_cats), int(url_id)))
        self.get_conn().commit()

    def delete_url(self, url_id: str) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'UPDATE urls SET is_deleted = ? WHERE id = ? AND is_deleted = 0',
            (int(time.time()), int(url_id),)
        )
        self.get_conn().commit()

    def get_all_urls(self) -> List[URL]:
        cursor = self.get_conn().cursor()
        cursor.execute(
            '''SELECT
                u.id AS id,
                u.hostname,
                u.description,
                u.bc_cats,
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
