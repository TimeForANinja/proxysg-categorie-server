import json
import sqlite3
import time
from contextlib import AbstractContextManager
from typing import Optional, List, Callable, Any

from auth.auth_user import AuthUser
from db.backend.abc.task import TaskDBInterface
from db.dbmodel.task import MutableTask, Task


def _build_task(row: Any) -> Task:
    """Parse SQLite row into a Task object."""
    param_obj = json.loads(row[3])

    return Task(
        id=str(row[0]),
        name=row[1],
        user=AuthUser.unserialize(row[2]),
        parameters=param_obj,
        status=row[4],
        created_at=row[5],
        updated_at=row[6],
    )


class SQLiteTask(TaskDBInterface):
    def __init__(
            self,
            get_cursor: Callable[[], AbstractContextManager[sqlite3.Cursor]]
        ):
        self.get_cursor = get_cursor

    def add_task(self, user: AuthUser, task: MutableTask) -> Task:
        current_timestamp = int(time.time())
        param_str = json.dumps(task.parameters)

        with self.get_cursor() as cursor:
            cursor.execute(
                '''INSERT INTO tasks 
                   (name, user, parameters, status, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (task.name, AuthUser.serialize(user), param_str, 'pending', current_timestamp, current_timestamp)
            )

            new_task = Task(
                id=str(cursor.lastrowid),
                name=task.name,
                user=user,
                parameters=task.parameters,
                status='pending',
                created_at=current_timestamp,
                updated_at=current_timestamp,
            )
            return new_task

    def get_task(self, task_id: str) -> Optional[Task]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT id, name, user, parameters, status, created_at, updated_at
                   FROM tasks
                   WHERE id = ?''',
                (int(task_id),)
            )
            row = cursor.fetchone()
        if not row:
            return None
        return _build_task(row)

    def update_task_status(self, task_id: str, status: str) -> Task:
        current_timestamp = int(time.time())
        with self.get_cursor() as cursor:
            cursor.execute(
                '''UPDATE tasks 
                   SET status = ?, updated_at = ? 
                   WHERE id = ?''',
                (status, current_timestamp, int(task_id))
            )
        return self.get_task(task_id)

    def get_all_tasks(self) -> List[Task]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT id, name, user, parameters, status, created_at, updated_at
                   FROM tasks'''
            )
            rows = cursor.fetchall()
        return [_build_task(row) for row in rows]

    def get_next_pending_task(self) -> Optional[Task]:
        with self.get_cursor() as cursor:
            cursor.execute(
                '''SELECT id, name, user, parameters, status, created_at, updated_at
                   FROM tasks
                   WHERE status = 'pending' '''
            )
            row = cursor.fetchone()
        if not row:
            return None
        return _build_task(row)
