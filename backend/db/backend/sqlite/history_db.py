import sqlite3
import time
from contextlib import AbstractContextManager
from typing import List, Callable, Optional

from auth.auth_user import AuthUser
from db.backend.abc.util.types import MyTransactionType
from db.backend.abc.history import HistoryDBInterface
from db.backend.sqlite.util.groups import split_opt_str_group, join_str_group
from db.dbmodel.history import History, Atomic


class SQLiteHistory(HistoryDBInterface):
    def __init__(
        self,
        get_cursor: Callable[[], AbstractContextManager[sqlite3.Cursor]]
    ):
        self.get_cursor = get_cursor

    def add_history_event(
        self,
        action: str,
        user: AuthUser,
        ref_token: List[str],
        ref_url: List[str],
        ref_category: List[str],
        atomics: Optional[List[Atomic]] = None,
        session: Optional[MyTransactionType] = None,
    ) -> History:
        """
        Add a new history event with the given name

        :param action: The action to be recorded
        :param user: The user who performed the action
        :param ref_token: List of token IDs referenced by the action
        :param ref_url: List of URL IDs referenced by the action
        :param ref_category: List of category IDs referenced by the action
        :param atomics: Optional list of atomic changes
        :param session: Optional database session to use
        :return: The newly created history event
        """
        timestamp = int(time.time())

        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT INTO history (time, description, user, ref_token, ref_url, ref_category) VALUES (?, ?, ?, ?, ?, ?)',
                (timestamp, action, AuthUser.serialize(user), join_str_group(ref_token), join_str_group(ref_url), join_str_group(ref_category))
            )
            history_id = cursor.lastrowid

            # Add atomics if provided
            atomics_list = atomics or []
            if atomics_list:
                # build params and insert into DB
                params = [
                    (
                        atomic.id,
                        AuthUser.serialize(atomic.user),
                        history_id,
                        atomic.action,
                        atomic.description or '',
                        atomic.time,
                        join_str_group(atomic.ref_token),
                        join_str_group(atomic.ref_url),
                        join_str_group(atomic.ref_category)
                    )
                    for atomic in atomics_list
                ]
                cursor.executemany(
                    'INSERT INTO atomics (id, user, history_id, action, description, time, ref_token, ref_url, ref_category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    params,
                )

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
        with self.get_cursor() as cursor:
            # Get all history events
            cursor.execute('SELECT id, time, description, user, ref_token, ref_url, ref_category FROM history')
            history_rows = cursor.fetchall()

            # Get all atomics in a single query
            cursor.execute('SELECT id, user, history_id, action, description, time, ref_token, ref_url, ref_category FROM atomics')
            atomics_rows = cursor.fetchall()

        # Group atomics by history_id
        atomics_by_history = {}
        for atomic_row in atomics_rows:
            atomic = Atomic(
                id=atomic_row[0],
                user=AuthUser.unserialize(atomic_row[1]),
                action=atomic_row[3],
                description=atomic_row[4] if atomic_row[4] else None,
                time=atomic_row[5],
                ref_token=split_opt_str_group(atomic_row[6]),
                ref_url=split_opt_str_group(atomic_row[7]),
                ref_category=split_opt_str_group(atomic_row[8]),
            )
            atomics_by_history.setdefault(atomic_row[2], []).append(atomic)

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

