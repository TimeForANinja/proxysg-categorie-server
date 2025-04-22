import sqlite3
import time
from typing import List, Callable

from auth.auth_user import AuthUser
from db.history import HistoryDBInterface, History
from db.sqlite.util.metadata import fetch_table_list


class SQLiteHistory(HistoryDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def add_history_event(self, action: str, user: AuthUser) -> History:
        cursor = self.get_conn().cursor()
        timestamp = int(time.time())
        cursor.execute(
            'INSERT INTO history (time, description, user) VALUES (?, ?, ?)',
            (timestamp, action, user.username,)
        )
        self.get_conn().commit()

        hist = History(
            id = str(cursor.lastrowid),
            time = timestamp,
            description = action,
            atomics = [],
            user = user.username,
        )
        return hist

    def get_history_events(self) -> List[History]:
        cursor = self.get_conn().cursor()
        cursor.execute('SELECT id, time, description, user FROM history')
        rows = cursor.fetchall()
        return [History(
            id = row[0],
            time = row[1],
            description = row[2],
            atomics = [],
            user = row[3],
        ) for row in rows]
