from dataclasses import field, dataclass
from enum import IntFlag
from typing import List
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from auth.auth_user import AuthUser
from db.util.validators import simpleNameValidator
from routes.restmodel.task import RESTTask
from db.util.schema import desc


@dataclass(kw_only=True)
class MutableTask:
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        **desc('Name of the task'),
    })
    parameters: List[str] = field(
        default_factory=list,
        metadata=desc('Parameters for the task'),
    )


@dataclass
class Task:
    """Helper class to represent a task."""
    id: str
    name: str
    user: AuthUser
    parameters: List[str]
    status: str
    created_at: int
    updated_at: int

    def to_rest(self) -> RESTTask:
        # hide "parameters" due to large size for e.g. import tasks
        return RESTTask(
            id=self.id,
            name=self.name,
            user=self.user.username,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


mutable_task_schema = class_schema(MutableTask)()
task_schema = class_schema(Task)()


class CleanupFlags(IntFlag):
    """FLags to define which Cleanups to run in a cleanup task"""
    Categories = 1 << 0
    URLs = 1 << 1
