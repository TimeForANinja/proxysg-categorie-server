import sqlite3
import time
from typing import List, Callable

from db.history import HistoryDBInterface, History
from db.sqlite.util.metadata import fetch_table_list


class SQLiteHistory(HistoryDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def add_history_event(self, action: str) -> History:
        cursor = self.get_conn().cursor()
        timestamp = int(time.time())
        cursor.execute(
            'INSERT INTO history (time, description) VALUES (?, ?)',
            (timestamp, action)
        )
        self.get_conn().commit()

        hist = History(
            id = str(cursor.lastrowid),
            time = timestamp,
            description = action,
            atomics = [],
        )
        return hist

    def get_history_events(self) -> List[History]:
        cursor = self.get_conn().cursor()
        cursor.execute('SELECT id, time, description FROM history')
        rows = cursor.fetchall()
        return [History(
            id = row[0],
            time = row[1],
            description = row[2],
            atomics = [],
        ) for row in rows]
