from apiflask.fields import List, Nested
from marshmallow_dataclass import class_schema
from typing import List as tList

from routes.restmodel.history import RESTHistory
from routes.schemas.generic_output import GenericOutput


class ListHistoryOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[RESTHistory] = List(Nested(class_schema(RESTHistory)()), required=True, description='List of History Events')
