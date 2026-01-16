from dataclasses import dataclass, field
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from db.util.schema import desc


@dataclass
class CommitInput:
    """Class representing the commit message input"""
    message: str = field(metadata={
        'required': True,
        'validate': Length(min=1),
        **desc('Commit message describing the changes'),
    })


commit_input_schema = class_schema(CommitInput)()
