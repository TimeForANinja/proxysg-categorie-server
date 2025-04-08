import sqlite3
import time
from typing import List

from db.history import HistoryDBInterface, History
from db.sqlite.util.metadata import fetch_table_list


class SQLiteHistory(HistoryDBInterface):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.create_table()

    def create_table(self) -> None:
        has_tables = fetch_table_list(self.conn)

        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                            id INTEGER PRIMARY KEY,
                            time INTEGER NOT NULL,
                            description TEXT
        )''')
        self.conn.commit()

        # if the history table did not yet exist we enter a default event
        if "history" not in has_tables:
            self.add_history_event('Database created')

    def add_history_event(self, action: str) -> History:
        cursor = self.conn.cursor()
        timestamp = int(time.time())
        cursor.execute(
            'INSERT INTO history (time, description) VALUES (?, ?)',
            (timestamp, action)
        )
        self.conn.commit()

        hist = History(
            id = str(cursor.lastrowid),
            time = timestamp,
            description = action,
            atomics = [],
        )
        return hist

    def get_history_events(self) -> List[History]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, time, description FROM history')
        rows = cursor.fetchall()
        return [History(
            id = row[0],
            time = row[1],
            description = row[2],
            atomics = [],
        ) for row in rows]
