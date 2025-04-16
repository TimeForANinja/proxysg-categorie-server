from typing import List
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


class ExistingCat:
    """Class for a single category read from an existing Database file"""
    name: str
    urls: List[str]
    def __init__(self, name: str, urls: List[str]):
        self.name = name
        self.urls = urls
