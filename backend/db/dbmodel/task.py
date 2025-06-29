from dataclasses import field, dataclass
from typing import List
from marshmallow.validate import Length

from auth.auth_user import AuthUser
from db.util.validators import simpleNameValidator
from routes.restmodel.task import RESTTask


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
