from apiflask.fields import String
from dataclasses import dataclass
from marshmallow.validate import Length


@dataclass
class CommitInput:
    """Class representing the commit message input"""
    message: str = String(
        required=True,
        validate=Length(min=1),
        metadata={'description': 'Commit message describing the changes'},
    )
