import sqlite3
import time
from typing import Callable, List

from db.abc.staging import StagedChange, MutableStagedChange, StagingDBInterface


def _build_change(row: any) -> StagedChange:
    """Parse SQLite row into a StagedChange object."""
    return StagedChange(
        id=row[0],
        action=row[1],
        user=row[2],
        time=row[3],
        table=row[4],
        entity_id=row[5],
        data=row[6],
    )


class SQLiteStaging(StagingDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn
    
    def store_staged_change(self, change: MutableStagedChange) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute(
            'INSERT INTO staged_changes (action, user, timestamp, table_name, data) VALUES (?, ?, ?, ?, ?)',
            (change.action, change.user, int(time.time()), change.table, change.data),
        )
        self.get_conn().commit()

    def get_staged_changes(self) -> List[StagedChange]:
        cursor = self.get_conn().cursor()
        cursor.execute('SELECT (id, action, user, timestamp, table_name, entity_id, data) FROM staged_changes')
        rows = cursor.fetchall()
        return [_build_change(row) for row in rows]

    def clear_staged_changes(self) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute('DELETE FROM staged_changes')
        self.get_conn().commit()
