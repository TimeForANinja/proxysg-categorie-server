import sqlite3
import time
from typing import Optional, List, Callable, Any

from db.backend.abc.token import TokenDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.util.groups import split_opt_str_group
from db.dbmodel.token import MutableToken, Token
from db.backend.sqlite.util.query_builder import build_update_query


def _build_token(row: Any) -> Token:
    """Parse SQLite row into a Token object."""
    return Token(
        id=str(row[0]),
        token=row[1],
        description=row[2],
        last_use=row[3],
        is_deleted=0,
        categories=split_opt_str_group(row[4]),
        pending_changes=False,
    )


class SQLiteToken(TokenDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def add_token(
            self,
            token_id: str,
            uuid: str,
            mut_tok: MutableToken,
            session: MyTransactionType = None,
    ) -> Token:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT INTO tokens (id, token, description) VALUES (?, ?, ?)',
            (token_id, uuid, mut_tok.description)
        )
        self.get_conn().commit()

        new_token = Token(
            id=token_id,
            token=uuid,
            description=mut_tok.description,
            last_use=0,
            is_deleted=0,
            pending_changes=False,
        )
        return new_token

    def get_token(self, token_id: str, session: MyTransactionType = None) -> Optional[Token]:
        cursor = self.get_conn().cursor()
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
            (token_id,)
        )
        row = cursor.fetchone()
        if row:
            return _build_token(row)
        return None

    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        cursor = self.get_conn().cursor()
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

    def update_token(self, token_id: str, token: MutableToken, session: MyTransactionType = None) -> Token:
        updates, params = build_update_query(token, {
            'description': 'description',
        })

        if updates:
            query = f'UPDATE tokens SET {", ".join(updates)} WHERE id = ? AND is_deleted = 0'
            params.append(token_id)
            cursor = self.get_conn().cursor()
            cursor.execute(query, params)
            self.get_conn().commit()

        return self.get_token(token_id)

    def update_usage(self, token_id: str) -> None:
        cursor = self.get_conn().cursor()
        timestamp = int(time.time())
        cursor.execute(
            'UPDATE tokens SET last_use = ? WHERE id = ? AND is_deleted = 0',
            (timestamp, token_id,)
        )
        self.get_conn().commit()

    def roll_token(self, token_id: str, uuid: str, session: MyTransactionType = None) -> Token:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'UPDATE tokens SET token = ? WHERE id = ? AND is_deleted = 0',
            (uuid, token_id,)
        )
        self.get_conn().commit()

        return self.get_token(token_id)

    def delete_token(self, token_id: str, session: MyTransactionType = None) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'UPDATE tokens SET is_deleted = ? WHERE id = ? AND is_deleted = 0',
            (int(time.time()), token_id,)
        )
        self.get_conn().commit()

    def get_all_tokens(self, session: MyTransactionType = None) -> List[Token]:
        cursor = self.get_conn().cursor()
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
