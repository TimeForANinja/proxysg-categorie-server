from dataclasses import field, dataclass
from typing import Optional, List
from marshmallow.validate import Length

from db.util.validators import simpleNameValidator, simpleStringValidator


@dataclass(kw_only=True)
class MutableCategory:
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        'description': 'Name of the category',
    })
    color: int = field(metadata={
        'required': True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the category'
        },
    )

@dataclass(kw_only=True)
class Category(MutableCategory):
    """
    Helper class to represent a category.
    """
    id: str = field(metadata={
        'required': True,
        'description': 'ID of the category',
    })
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        'description': 'Name of the category',
    })
    color: int = field(metadata={
        'required': True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the category'
        },
    )
    is_deleted: int = field(
        default=0,
        metadata={
            'description': 'Whether the category is deleted or not',
        }
    )
    nested_categories: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of category IDs associated with the category',
        }
    )
