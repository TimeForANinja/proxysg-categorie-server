import sqlite3

from db.sqlite.util import split_opt_str_group
from db.url import URLDBInterface, MutableURL, URL
from typing import Optional, List


class SQLiteURL(URLDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                            id INTEGER PRIMARY KEY,
                            hostname TEXT NOT NULL,
                            description TEXT NOT NULL,
                            is_deleted INTEGER DEFAULT 0
        )''')
        self.conn.commit()

    def add_url(self, mut_url: MutableURL) -> URL:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO urls (hostname, description) VALUES (?, ?)',
            (mut_url.hostname,mut_url.description)
        )
        self.conn.commit()

        new_url = URL(
            hostname = mut_url.hostname,
            description=mut_url.description,
            id = str(cursor.lastrowid),
            is_deleted = 0,
        )
        return new_url

    def get_url(self, url_id: str) -> Optional[URL]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT
                u.id AS id,
                u.hostname,
                u.description,
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
            return URL(
                id=str(row[0]),
                hostname=row[1],
                description=row[2],
                is_deleted=0,
                categories=split_opt_str_group(row[3]),
            )
        return None

    def update_url(self, url_id: str, mut_url: MutableURL) -> URL:
        updates = []
        params = []

        # Prepare update query based on non-None fields
        if mut_url.hostname is not None:
            updates.append("hostname = ?")
            params.append(mut_url.hostname)
        if mut_url.description is not None:
            updates.append("description = ?")
            params.append(mut_url.description)

        if updates:
            query = f'UPDATE urls SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(int(url_id))
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()

        return self.get_url(url_id)

    def delete_url(self, url_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE urls SET is_deleted = 1 WHERE id = ? AND is_deleted = 0',
            (int(url_id),)
        )
        self.conn.commit()

    def get_all_urls(self) -> List[URL]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT
                u.id AS id,
                u.hostname,
                u.description,
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
        return [URL(
            id=str(row[0]),
            hostname=row[1],
            description=row[2],
            is_deleted=0,
            categories=split_opt_str_group(row[3]),
        ) for row in rows]
