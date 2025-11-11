import orjson
from typing import List, Tuple, Optional

from auth.auth_user import AuthUser
from db.backend.abc.util.types import MyTransactionType
from db.backend.abc.staging import StagingDBInterface
from db.backend.sqlite.util.cursor_callable import GetCursorProtocol
from db.dbmodel.staging import StagedChange, ActionTable, ActionType


def _build_change(row: Tuple) -> StagedChange:
    """Parse SQLite row into a StagedChange object."""
    data = orjson.loads(row[5]) if row[5] else None
    return StagedChange(
        action_type=ActionType(row[0]),
        action_table=ActionTable(row[1]),
        auth=AuthUser.unserialize(row[2]),
        uid=row[3],
        timestamp=int(row[4]),
        data=data,
    )


class SQLiteStaging(StagingDBInterface):
    def __init__(
        self,
        get_cursor: GetCursorProtocol
    ):
        self.get_cursor = get_cursor

    def store_staged_change(self, change: StagedChange):
        # Convert Enum values to their integer values
        action_value = change.action_type.value
        table_value = change.action_table.value

        # Serialize AuthUser to JSON string
        auth_json = AuthUser.serialize(change.auth)

        # Serialize data dictionary to JSON string
        data_json = str(orjson.dumps(change.data)) if change.data else None

        # push to db
        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT INTO staged_changes (action, user, timestamp, table_name, entity_id, data) VALUES (?, ?, ?, ?, ?, ?)',
                (action_value, auth_json, change.timestamp, table_value, change.uid, data_json),
            )

    def store_staged_changes(self, changes: List[StagedChange]):
        """Store a list of staged changes in the SQLite database (batch)."""
        if not changes:
            return

        params = [
            (
                ch.action_type.value,
                AuthUser.serialize(ch.auth),
                ch.timestamp,
                ch.action_table.value,
                ch.uid,
                str(orjson.dumps(ch.data)) if ch.data else None,
            )
            for ch in changes
        ]

        with self.get_cursor() as cursor:
            cursor.executemany(
                'INSERT INTO staged_changes (action, user, timestamp, table_name, entity_id, data) VALUES (?, ?, ?, ?, ?, ?)',
                params,
            )

    def get_staged_changes(self, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        with self.get_cursor(session=session) as cursor:
            cursor.execute('SELECT action, table_name, user, entity_id, timestamp, data FROM staged_changes')
            rows = cursor.fetchall()
        return [_build_change(row) for row in rows]

    def get_staged_changes_by_table(self, table: ActionTable, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        with self.get_cursor(session=session) as cursor:
            cursor.execute('SELECT action, table_name, user, entity_id, timestamp, data FROM staged_changes WHERE table_name = ?', (table.value,))
            rows = cursor.fetchall()
        return [_build_change(row) for row in rows]

    def get_staged_changes_by_table_and_id(
        self,
        table: ActionTable,
        obj_id: str,
        session: Optional[MyTransactionType] = None,
    ) -> List[StagedChange]:
        with self.get_cursor(session=session) as cursor:
            cursor.execute('SELECT action, table_name, user, entity_id, timestamp, data FROM staged_changes WHERE table_name = ? AND entity_id = ?', (table.value, obj_id))
            rows = cursor.fetchall()
        return [_build_change(row) for row in rows]

    def clear_staged_changes(self, before: int = None, session: Optional[MyTransactionType] = None):
        with self.get_cursor(session=session) as cursor:
            if before is not None:
                cursor.execute('DELETE FROM staged_changes WHERE timestamp <= ?', (before,))
            else:
                # noinspection SqlWithoutWhere
                cursor.execute('DELETE FROM staged_changes')
