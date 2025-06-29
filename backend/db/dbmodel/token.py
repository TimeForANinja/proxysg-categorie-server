from dataclasses import field, dataclass
from typing import List
from marshmallow.validate import Length

from db.util.validators import simpleStringValidator


@dataclass(kw_only=True)
class MutableToken:
    description: str = field(metadata={
        'required': True,
        'validate': [
            Length(max=255),
            simpleStringValidator,
        ],
        'description': 'Description of the token'
    })


@dataclass(kw_only=True)
class Token(MutableToken):
    """
    Helper class to represent a token.
    """
    id: str = field(metadata={
        'required': True,
        'description': 'ID of the token',
    })
    token: str = field(metadata={
        'required': True,
        # uuid v4 is always 36 characters
        'validate': Length(min=36, max=36),
        'description': 'Token for use with the API',
    })
    description: str = field(metadata={
        'required': True,
        'validate': [
            Length(max=255),
            simpleStringValidator,
        ],
        'description': 'Description of the token'
    })
    last_use: int = field(
        default=0,
        metadata={
            'description': 'Timestamp when the token was last used',
        }
    )
    is_deleted: int = field(
        default=0,
        metadata={
            'description': 'Whether the token is deleted or not',
        }
    )
    categories: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of category IDs associated with the URL',
        }
    )
