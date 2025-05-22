import sqlite3
import time
from typing import List, Callable

from auth.auth_user import AuthUser
from db.abc.history import HistoryDBInterface, History
from db.sqlite.util.groups import split_opt_str_group


class SQLiteHistory(HistoryDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def add_history_event(
            self,
            action: str,
            user: AuthUser,
            ref_token: List[str],
            ref_url: List[str],
            ref_category: List[str],
    ) -> History:
        """
        Add a new history event with the given name

        :param action: The action to be recorded
        :param user: The user who performed the action
        :param ref_token: List of token IDs referenced by the action
        :param ref_url: List of URL IDs referenced by the action
        :param ref_category: List of category IDs referenced by the action
        :return: The newly created history event
        """
        cursor = self.get_conn().cursor()
        timestamp = int(time.time())
        cursor.execute(
            'INSERT INTO history (time, description, user, ref_token, ref_url, ref_category) VALUES (?, ?, ?, ?, ?, ?)',
            (timestamp, action, user.username, ','.join(ref_token), ','.join(ref_url), ','.join(ref_category))
        )
        self.get_conn().commit()

        hist = History(
            id=str(cursor.lastrowid),
            time=timestamp,
            description=action,
            atomics=[],
            user=user.username,
            ref_token=ref_token,
            ref_url=ref_url,
            ref_category=ref_category,
        )
        return hist

    def get_history_events(self) -> List[History]:
        cursor = self.get_conn().cursor()
        cursor.execute('SELECT id, time, description, user, ref_token, ref_url, ref_category FROM history')
        rows = cursor.fetchall()
        return [History(
            id=str(row[0]),
            time=row[1],
            description=row[2],
            atomics=[],
            user=row[3],
            ref_token=split_opt_str_group(row[4]),
            ref_url=split_opt_str_group(row[5]),
            ref_category=split_opt_str_group(row[6]),
        ) for row in rows]
