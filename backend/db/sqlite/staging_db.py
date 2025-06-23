import json
import sqlite3
from typing import Callable, List, Tuple

from auth.auth_user import AuthUser
from db.abc.staging import StagedChange, StagingDBInterface, ActionType, ActionTable


def _build_change(row: Tuple) -> StagedChange:
    """Parse SQLite row into a StagedChange object."""
    data = json.loads(row[5]) if row[5] else None
    return StagedChange(
        action_type=ActionType(row[0]),
        action_table=ActionTable(row[1]),
        auth=AuthUser.unserialize(row[2]),
        uid=row[3],
        timestamp=int(row[4]),
        data=data,
    )


class SQLiteStaging(StagingDBInterface):
    def __init__(self, get_conn: Callable[[], sqlite3.Connection]):
        self.get_conn = get_conn

    def store_staged_change(self, change: StagedChange) -> None:
        cursor = self.get_conn().cursor()

        # Convert Enum values to their integer values
        action_value = change.action_type.value
        table_value = change.action_table.value

        # Serialize AuthUser to JSON string
        auth_json = AuthUser.serialize(change.auth)

        # Serialize data dictionary to JSON string
        data_json = json.dumps(change.data) if change.data else None

        cursor.execute(
            'INSERT INTO staged_changes (action, user, timestamp, table_name, entity_id, data) VALUES (?, ?, ?, ?, ?, ?)',
            (action_value, auth_json, change.timestamp, table_value, change.uid, data_json),
        )
        self.get_conn().commit()

    def get_staged_changes(self) -> List[StagedChange]:
        cursor = self.get_conn().cursor()
        cursor.execute('SELECT action, table_name, user, entity_id, timestamp, data FROM staged_changes')
        rows = cursor.fetchall()
        return [_build_change(row) for row in rows]

    def clear_staged_changes(self) -> None:
        cursor = self.get_conn().cursor()
        cursor.execute('DELETE FROM staged_changes')
        self.get_conn().commit()
