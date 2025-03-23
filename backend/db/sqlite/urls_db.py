import sqlite3
from db.urls import URLDBInterface, MutableURL, URL
from typing import Optional, List


class SQLURLs(URLDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                            id INTEGER PRIMARY KEY,
                            hostname TEXT NOT NULL,
                            is_deleted INTEGER DEFAULT 0
        )''')
        self.conn.commit()

    def add_url(self, mut_url: MutableURL) -> URL:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO urls (hostname) VALUES (?)',
            (mut_url.hostname,)
        )
        self.conn.commit()

        new_url = URL(
            hostname = mut_url.hostname,
            id = cursor.lastrowid,
            is_deleted = 0,
        )
        return new_url

    def get_url(self, url_id: int) -> Optional[URL]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT 
                    u.id AS id,
                    hostname,
                    GROUP_CONCAT(uc.category_id) as categories
                FROM urls u
                LEFT JOIN url_categories uc
                ON u.id = uc.url_id AND uc.is_deleted = 0
                WHERE u.id = ? AND u.is_deleted = 0
                GROUP BY u.id''',
            (url_id,)
        )
        row = cursor.fetchone()
        if row:
            return URL(
                id=row[0],
                hostname=row[1],
                is_deleted=0,
                categories=row[2].split(',') if row[2] else [],
            )
        return None

    def update_url(self, url_id: int, mut_url: MutableURL) -> URL:
        updates = []
        params = []

        # Prepare update query based on non-None fields
        if mut_url.hostname is not None:
            updates.append("hostname = ?")
            params.append(mut_url.hostname)

        if updates:
            query = f'UPDATE urls SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(url_id)
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()

        return self.get_url(url_id)

    def delete_url(self, url_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE urls SET is_deleted = 1 WHERE id = ? AND is_deleted = 0',
            (url_id,)
        )
        self.conn.commit()

    def get_all_urls(self) -> List[URL]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT
                u.id AS id,
                hostname,
                GROUP_CONCAT(uc.category_id) as categories
            FROM urls u
            LEFT JOIN url_categories uc
            ON u.id = uc.url_id AND uc.is_deleted = 0
            WHERE u.is_deleted = 0
            GROUP BY u.id''',
        )
        rows = cursor.fetchall()
        return [URL(
            id=row[0],
            hostname=row[1],
            is_deleted=0,
            categories=row[2].split(',') if row[2] else [],
        ) for row in rows]
