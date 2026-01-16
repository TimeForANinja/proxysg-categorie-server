from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from db.util.schema import desc


@dataclass
class RESTAtomic:
    """Helper class to represent an atomic change within a history event."""
    id: str = field(metadata={
        'required': True,
        **desc('ID of the category'),
    })
    user: str = field(metadata={
        'required': True,
        **desc('User who performed the action'),
    })
    action: str = field(metadata={
        'required': True,
        **desc('Action performed by the user'),
    })
    description: str = field(metadata={
        'required': True,
        **desc('Description of the category'),
    })
    timestamp: int = field(metadata={
        'required': True,
        **desc('Timestamp of the event'),
    })
    ref_token: List[str] = field(default_factory=list)
    ref_url: List[str] = field(default_factory=list)
    ref_category: List[str] = field(default_factory=list)


@dataclass
class RESTHistory:
    """Helper class to represent a category."""
    id: str = field(metadata={
        'required': True,
        **desc('ID of the category'),
    })
    time: int = field(metadata={
        'required': True,
        **desc('Timestamp of the event'),
    })
    user: str = field(metadata={
        'required': True,
        **desc('User who performed the action'),
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            'validate': Length(max=255),
            **desc('Description of the category'),
        },
    )
    ref_token: List[str] = field(default_factory=list)
    ref_url: List[str] = field(default_factory=list)
    ref_category: List[str] = field(default_factory=list)
    atomics: List[RESTAtomic] = field(default_factory=list)


rest_history_schema = class_schema(RESTHistory)()
