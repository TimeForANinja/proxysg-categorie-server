import time
from typing import Optional, List, Mapping, Any
from bson.objectid import ObjectId
from pymongo.synchronous.database import Database

from auth.auth_user import AuthUser
from db.task import TaskDBInterface, MutableTask, Task


def _build_task(row: Mapping[str, Any]) -> Task:
    """build a Task object from a MongoDB document"""
    return Task(
        id=str(row['_id']),
        name=row['name'],
        user=row['user'],
        parameters=row.get('parameters'),
        status=row['status'],
        created_at=row['created_at'],
        updated_at=row['updated_at'],
    )


class MongoDBTask(TaskDBInterface):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        self.db = db
        self.collection = self.db['tasks']

    def add_task(self, user: AuthUser, task: MutableTask) -> Task:
        current_timestamp = int(time.time())
        result = self.collection.insert_one({
            'name': task.name,
            'user': user.username,
            'parameters': task.parameters,
            'status': 'pending',
            'created_at': current_timestamp,
            'updated_at': current_timestamp,
        })

        return Task(
            id=str(result.inserted_id),
            name=task.name,
            user=user.username,
            parameters=task.parameters,
            status='pending',
            created_at=current_timestamp,
            updated_at=current_timestamp,
        )

    def get_task(self, task_id: str) -> Optional[Task]:
        query = {'_id': ObjectId(task_id)}
        row = self.collection.find_one(query)
        if not row:
            return None

        return _build_task(row)

    def update_task_status(self, task_id: str, status: str) -> Task:
        current_timestamp = int(time.time())
        query = {'_id': ObjectId(task_id)}
        update_fields = {
            'status': status,
            'updated_at': current_timestamp,
        }

        result = self.collection.update_one(query, {'$set': update_fields})

        if result.matched_count == 0:
            raise ValueError(f'Task with ID {task_id} not found or is deleted.')

        # Return the updated task
        return self.get_task(task_id)

    def get_all_tasks(self) -> List[Task]:
        rows = self.collection.find()
        return [
            _build_task(row)
            for row in rows
        ]

    def get_next_pending_task(self) -> Optional[Task]:
        row = self.collection.find_one({'status': 'pending'})
        if not row:
            return None

        return _build_task(row)
