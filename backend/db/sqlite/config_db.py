import sqlite3
from typing import Optional, Callable


CONFIG_VAR_SCHEMA_VERSION = 'schema-version'


class SQLiteConfig:
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def read_int(self, key: str) -> int:
        """Get the value of a config variable, or -1 if it doesn't exist."""
        cursor = self.get_conn().cursor()
        cursor.execute(
            'SELECT value FROM config WHERE key = ?',
            (key,)
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])
        else:
            return -1

    def set_int(self, key: str, value: int) -> None:
        """Set a config variable. If it doesn't exist, create it."""
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)',
            (key, str(value))
        )
        self.get_conn().commit()

    def get_schema_version(self) -> int:
        """
        Get the current schema version from the config table.
        Defaults to 0 if the table/value doesn't exist yet.
        """
        try:
            val = self.read_int(CONFIG_VAR_SCHEMA_VERSION)
        except sqlite3.OperationalError as e:
            # table does not exist yet, which means we default to version 0
            if 'no such table' in str(e):
                return 0
            # other error -> exit
            raise
        # all values <0 are invalid, so we default to "no table"=0
        return max(val, 0)
