from dataclasses import field, dataclass
from marshmallow.validate import Length

from db.util.validators import simpleNameValidator
from db.util.schema import desc


@dataclass(kw_only=True)
class RESTTask:
    """
    Helper class to represent a task.
    """
    id: str = field(metadata={
        'required': True,
        **desc('ID of the task'),
    })
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        **desc('Name of the task'),
    })
    user: str = field(metadata={
        'required': True,
        **desc('User who performed the action'),
    })
    status: str = field(
        default="pending",
        metadata=desc('Status of the task (pending, running, success, failed)'),
    )
    created_at: int = field(
        default=0,
        metadata=desc('Timestamp when the task was created'),
    )
    updated_at: int = field(
        default=0,
        metadata=desc('Timestamp when the task was last updated'),
    )
