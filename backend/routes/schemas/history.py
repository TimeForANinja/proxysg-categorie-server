from apiflask.fields import List, Nested
from marshmallow_dataclass import class_schema
from typing import List as tList

from db.abc.history import History
from routes.schemas.generic_output import GenericOutput


class ListHistoryOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[History] = List(Nested(class_schema(History)()), required=True, description='List of History Events')
