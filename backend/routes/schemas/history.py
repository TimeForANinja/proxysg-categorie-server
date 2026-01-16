from apiflask.fields import List, Nested
from typing import List as tList

from db.util.schema import desc
from routes.restmodel.history import RESTHistory, rest_history_schema
from routes.schemas.generic_output import GenericOutput


class ListHistoryOutput(GenericOutput):
    """Output schema for a list of history events"""
    data: tList[RESTHistory] = List(
        Nested(rest_history_schema),
        required=True,
        metadata=desc('List of History Events'),
    )
