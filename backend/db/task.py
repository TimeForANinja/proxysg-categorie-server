from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length
from enum import IntFlag

from auth.auth_user import AuthUser
from db.util.validators import simpleNameValidator


@dataclass(kw_only=True)
class MutableTask:
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        'description': 'Name of the task',
    })
    parameters: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'Parameters for the task'
        },
    )

@dataclass(kw_only=True)
class Task(MutableTask):
    """
    Helper class to represent a task.
    """
    id: str = field(metadata={
        'required': True,
        'description': 'ID of the task',
    })
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        'description': 'Name of the task',
    })
    user: str = field(metadata={
        'required': True,
        'description': 'User who performed the action',
    })
    parameters: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'Parameters for the task'
        },
    )
    status: str = field(
        default="pending",
        metadata={
            'description': 'Status of the task (pending, running, success, failed)',
        }
    )
    created_at: int = field(
        default=0,
        metadata={
            'description': 'Timestamp when the task was created',
        }
    )
    updated_at: int = field(
        default=0,
        metadata={
            'description': 'Timestamp when the task was last updated',
        }
    )


class TaskDBInterface(ABC):
    @abstractmethod
    def add_task(self, user: AuthUser, task: MutableTask) -> Task:
        """
        Add a new task with the given name, description, and parameters.

        :param user: The user who performed the action.
        :param task: The (partial) task to add.
        :return: The newly created task.
        """
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieve the details of a specific task by its ID.

        :param task_id: The ID of the task to retrieve.
        :return: A Task
                 or None if the task doesn't exist or is marked as deleted.
        """
        pass

    @abstractmethod
    def update_task_status(
            self,
            task_id: str,
            status: str,
    ) -> Task:
        """
        Update the status of a specific task.

        :param task_id: The ID of the task to update.
        :param status: The new status of the task.
        """
        pass

    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all active tasks that are not marked as deleted.

        :return: A list of tasks
        """
        pass

    @abstractmethod
    def get_next_pending_task(self) -> Optional[Task]:
        """
        Get the next pending task.

        :return: A Task object or None if no pending tasks are available.
        """
        pass


class CleanupFlags(IntFlag):
    """FLags to define which Cleanups to run in a cleanup task"""
    Categories = 1 << 0
    URLs = 1 << 1
