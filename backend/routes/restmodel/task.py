from dataclasses import field, dataclass
from typing import List
from marshmallow.validate import Length

from db.util.validators import simpleNameValidator


@dataclass(kw_only=True)
class RESTTask:
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
