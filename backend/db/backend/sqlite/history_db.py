import sqlite3
import time
from contextlib import AbstractContextManager
from typing import List, Callable, Optional, Any

from auth.auth_user import AuthUser
from db.backend.abc.util.types import MyTransactionType
from db.backend.abc.history import HistoryDBInterface
from db.backend.sqlite.util.groups import split_opt_str_group, join_str_group
from db.dbmodel.history import History, Atomic


def _build_atomic(row: Any) -> Atomic:
    """Parse SQLite row into an Atomic object."""
    return Atomic(
        id=row[0],
        user=AuthUser.unserialize(row[1]),
        action=row[3],
        description=row[4] if row[4] else None,
        time=row[5],
        ref_token=split_opt_str_group(row[6]),
        ref_url=split_opt_str_group(row[7]),
        ref_category=split_opt_str_group(row[8]),
    )


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

        # TODO: don't forget to add back session, when finally implementing it for sqlite
        self._add_atomics(history_id, atomics)

        return History(
            id=str(history_id),
            time=timestamp,
            description=action,
            atomics=atomics or [],
            user=user,
            ref_token=ref_token,
            ref_url=ref_url,
            ref_category=ref_category,
        )

    def _add_atomics(
        self,
        history_id: Any,
        atomics: Optional[List[Atomic]],
    ):
        """Utility method to insert atomics for a given history event."""
        if not atomics:
            return
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
            for atomic in atomics
        ]
        with self.get_cursor() as cursor:
            cursor.executemany(
                'INSERT INTO atomics (id, user, history_id, action, description, time, ref_token, ref_url, ref_category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                params,
            )

    def get_history_events(self, include_atomics: bool = False) -> List[History]:
        with self.get_cursor() as cursor:
            # Get all history events
            cursor.execute('SELECT id, time, description, user, ref_token, ref_url, ref_category FROM history')
            history_rows = cursor.fetchall()

            # fetch all atomics
            # if include_atomics is false, this will simply be an empty list but not break future code
            atomics_rows = []
            if include_atomics:
                # Get all atomics in a single query
                cursor.execute('SELECT id, user, history_id, action, description, time, ref_token, ref_url, ref_category FROM atomics')
                atomics_rows = cursor.fetchall()

        # Group atomics by history_id
        atomics_by_history: dict[Any, List[Atomic]] = {}
        for atomic_row in atomics_rows:
            atomics_by_history.setdefault(atomic_row[2], []).append(_build_atomic(atomic_row))

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

    def get_history_atomics(
        self,
        references_history: Optional[List[str]] = None,
        references_url: Optional[List[str]] = None,
        references_token: Optional[List[str]] = None,
        references_category: Optional[List[str]] = None,
    ) -> List[Atomic]:
        # if __only__ references_history is given, we can use a more efficient query
        if references_history and (not references_url and not references_token and not references_category):
            with self.get_cursor() as cursor:
                cursor.execute(
                    'SELECT id, user, history_id, action, description, time, ref_token, ref_url, ref_category FROM atomics WHERE history_id IN (?)',
                    references_history
                )
                atomics_rows = cursor.fetchall()
                return [
                    _build_atomic(row)
                    for row in atomics_rows
                ]

        # if other parameters are (also) provided, we're unfortunately screwed
        # we have to fetch all atomics and filter in python
        # this is required since we're using composited items for ref_token, ref_url and ref_category
        # that means that we're violating the 1NF (search for Database normalization -> Normal forms for details),
        # which results in limited possibilities when querying

        with self.get_cursor() as cursor:
            cursor.execute('SELECT id, user, history_id, action, description, time, ref_token, ref_url, ref_category FROM atomics')
            atomics_rows = cursor.fetchall()

        res = []
        for row in atomics_rows:
            # check if the atomic matches any of the given conditions
            a = _build_atomic(row)
            if str(row[2]) in references_history:
                res.append(a)
            elif set(references_url) & set(a.ref_url):
                res.append(a)
            elif set(references_token) & set(a.ref_token):
                res.append(a)
            elif set(references_category) & set(a.ref_category):
                res.append(a)

        return res
