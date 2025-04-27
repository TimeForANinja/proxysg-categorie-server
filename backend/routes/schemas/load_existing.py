from apiflask.fields import String
from dataclasses import dataclass
from marshmallow.validate import Length


@dataclass
class ExistingDBInput:
    """Class representing the DB Structure loaded from an existing DB File"""
    categoryDB: str = String(
        required=True,
        validate=Length(min=1),
        metadata={'description': 'Content of the existing category DB'},
    )
    prefix: str = String(
        required=True,
        validate=Length(min=1),
        metadata={'description': 'Prefix of the existing category DB'},
    )
