import sqlite3
import time
from typing import List, Callable, Optional

from auth.auth_user import AuthUser
from db.abc.history import HistoryDBInterface, History, Atomic
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
            atomics: Optional[List[Atomic]] = None,
    ) -> History:
        """
        Add a new history event with the given name

        :param action: The action to be recorded
        :param user: The user who performed the action
        :param ref_token: List of token IDs referenced by the action
        :param ref_url: List of URL IDs referenced by the action
        :param ref_category: List of category IDs referenced by the action
        :param atomics: Optional list of atomic changes
        :return: The newly created history event
        """
        cursor = self.get_conn().cursor()
        timestamp = int(time.time())
        cursor.execute(
            'INSERT INTO history (time, description, user, ref_token, ref_url, ref_category) VALUES (?, ?, ?, ?, ?, ?)',
            (timestamp, action, AuthUser.serialize(user), ','.join(ref_token), ','.join(ref_url), ','.join(ref_category))
        )
        history_id = cursor.lastrowid

        # Add atomics if provided
        atomics_list = atomics or []
        for atomic in atomics_list:
            cursor.execute(
                'INSERT INTO atomics (user, history_id, action, description, time, ref_token, ref_url, ref_category) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (AuthUser.serialize(atomic.user), history_id, atomic.action, atomic.description or '', atomic.timestamp, ','.join(atomic.ref_token), ','.join(atomic.ref_url), ','.join(atomic.ref_category))
            )
            atomic.id = str(cursor.lastrowid)

        self.get_conn().commit()

        hist = History(
            id=str(history_id),
            time=timestamp,
            description=action,
            atomics=atomics_list,
            user=user,
            ref_token=ref_token,
            ref_url=ref_url,
            ref_category=ref_category,
        )
        return hist

    def get_history_events(self) -> List[History]:
        cursor = self.get_conn().cursor()

        # Get all history events
        cursor.execute('SELECT id, time, description, user, ref_token, ref_url, ref_category FROM history')
        history_rows = cursor.fetchall()

        # Get all atomics in a single query
        cursor.execute('SELECT id, history_id, user, action, description, time, ref_token, ref_url, ref_category FROM atomics')
        atomics_rows = cursor.fetchall()

        # Group atomics by history_id
        atomics_by_history = {}
        for atomic_row in atomics_rows:
            history_id = atomic_row[1]
            atomic = Atomic(
                id=str(atomic_row[0]),
                user=AuthUser.unserialize(atomic_row[2]),
                action=atomic_row[3],
                description=atomic_row[4] if atomic_row[4] else None,
                timestamp=atomic_row[5],
                ref_token=split_opt_str_group(atomic_row[6]),
                ref_url=split_opt_str_group(atomic_row[7]),
                ref_category=split_opt_str_group(atomic_row[8]),
            )
            atomics_by_history.setdefault(history_id, []).append(atomic)

        # Create History objects with their associated atomics
        result = []
        for row in history_rows:
            history_id = row[0]
            result.append(History(
                id=str(history_id),
                time=row[1],
                description=row[2],
                atomics=atomics_by_history.get(history_id, []),
                user=AuthUser.unserialize(row[3]),
                ref_token=split_opt_str_group(row[4]),
                ref_url=split_opt_str_group(row[5]),
                ref_category=split_opt_str_group(row[6]),
            ))

        return result

