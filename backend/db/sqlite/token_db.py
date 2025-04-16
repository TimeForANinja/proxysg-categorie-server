import sqlite3
import time
from typing import Optional, List

from db.sqlite.util.groups import split_opt_str_group
from db.token import TokenDBInterface, MutableToken, Token


def _build_token(row: any) -> Token:
    """Parse SQLite row into Token object."""
    return Token(
        id=str(row[0]),
        token=row[1],
        description=row[2],
        last_use=row[3],
        is_deleted=0,
        categories=split_opt_str_group(row[4]),
    )


class SQLiteToken(TokenDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                            id INTEGER PRIMARY KEY,
                            token TEXT NOT NULL,
                            description TEXT NOT NULL,
                            last_use INTEGER DEFAULT 0,
                            is_deleted INTEGER DEFAULT 0
        )''')
        self.conn.commit()

    def add_token(self, uuid: str, mut_tok: MutableToken) -> Token:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO tokens (token, description) VALUES (?, ?)',
            (uuid, mut_tok.description)
        )
        self.conn.commit()

        new_token = Token(
            id=str(cursor.lastrowid),
            token=uuid,
            description=mut_tok.description,
            last_use=0,
            is_deleted=0,
        )
        return new_token

    def get_token(self, token_id: str) -> Optional[Token]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT
                t.id AS id,
                t.token,
                t.description,
                t.last_use,
                GROUP_CONCAT(tc.category_id) as categories
            FROM tokens t
            LEFT JOIN (
                SELECT
                    tc.token_id,
                    tc.category_id
                FROM token_categories tc
                INNER JOIN categories c
                ON tc.category_id = c.id
                WHERE c.is_deleted = 0 AND tc.is_deleted = 0
            ) tc
            ON t.id = tc.token_id
            WHERE t.is_deleted = 0 AND t.id = ?
            GROUP BY t.id''',
            (int(token_id),)
        )
        row = cursor.fetchone()
        if row:
            return _build_token(row)
        return None

    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT
                t.id AS id,
                t.token,
                t.description,
                t.last_use,
                GROUP_CONCAT(tc.category_id) as categories
            FROM tokens t
            LEFT JOIN (
                SELECT
                    tc.token_id,
                    tc.category_id
                FROM token_categories tc
                INNER JOIN categories c
                ON tc.category_id = c.id
                WHERE c.is_deleted = 0 AND tc.is_deleted = 0
            ) tc
            ON t.id = tc.token_id
            WHERE t.is_deleted = 0 AND t.token = ?
            GROUP BY t.id''',
            (token_uuid,)
        )
        row = cursor.fetchone()
        if row:
            return _build_token(row)
        return None

    def update_token(self, token_id: str, token: MutableToken) -> Token:
        updates = []
        params = []

        # Prepare an update query based on non-None fields
        if token.description is not None:
            updates.append('description = ?')
            params.append(token.description)

        if updates:
            query = f'UPDATE tokens SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(token_id)
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()

        return self.get_token(token_id)

    def update_usage(self, token_id: str) -> None:
        cursor = self.conn.cursor()
        timestamp = int(time.time())
        cursor.execute(
            'UPDATE tokens SET last_use = ? WHERE id = ? AND is_deleted = 0',
            (timestamp, int(token_id),)
        )
        self.conn.commit()

    def roll_token(self, token_id: str, uuid: str) -> Token:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE tokens SET token = ? WHERE id = ? AND is_deleted = 0',
            (uuid, int(token_id),)
        )
        self.conn.commit()

        return self.get_token(token_id)

    def delete_token(self, token_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE tokens SET is_deleted = 1 WHERE id = ? AND is_deleted = 0',
            (int(token_id),)
        )
        self.conn.commit()

    def get_all_tokens(self) -> List[Token]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT
                t.id AS id,
                t.token,
                t.description,
                t.last_use,
                GROUP_CONCAT(tc.category_id) as categories
            FROM tokens t
            LEFT JOIN (
                SELECT
                    tc.token_id,
                    tc.category_id
                FROM token_categories tc
                INNER JOIN categories c
                ON tc.category_id = c.id
                WHERE c.is_deleted = 0 AND tc.is_deleted = 0
            ) tc
            ON t.id = tc.token_id
            WHERE t.is_deleted = 0
            GROUP BY t.id''',
        )
        rows = cursor.fetchall()
        return [_build_token(row) for row in rows]
