from typing import List, Optional

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.task import MutableTask, Task
from db.stagingdb.cache import StagedCollection


class StagingDBTask:
    def __init__(self, db: DBInterface, staged: StagedCollection):
        self._db = db
        self._staged = staged

    def add_task(self, user: AuthUser, task: MutableTask) -> Task:
        return self._db.tasks.add_task(user, task)

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._db.tasks.get_task(task_id)

    def update_task_status(
            self,
            task_id: str,
            status: str,
    ) -> Task:
        return self._db.tasks.update_task_status(task_id, status)

    def get_all_tasks(self) -> List[Task]:
        return self._db.tasks.get_all_tasks()

    def get_next_pending_task(self) -> Optional[Task]:
        return self._db.tasks.get_next_pending_task()
