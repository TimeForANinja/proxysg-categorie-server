from apiflask.fields import List, Nested
from marshmallow_dataclass import class_schema
from typing import List as tList
from dataclasses import field, dataclass

from routes.restmodel.history import RESTHistory, RESTAtomic
from routes.schemas.generic_output import GenericOutput


@dataclass
class GetHistoryQuery:
    """Query params for listing history events"""
    include_atomics: bool = field(
        default=False,
        metadata={
            'description': "When true, include atomics in each history event. Default: false",
            'example': False,
        }
    )


class ListHistoryOutput(GenericOutput):
    """Output schema for a list of history events"""
    data: tList[RESTHistory] = List(Nested(class_schema(RESTHistory)()), required=True, description='List of History Events')


class ListAtomicsOutput(GenericOutput):
    """Output schema for a list of atomics"""
    data: tList[RESTAtomic] = List(Nested(class_schema(RESTAtomic)()), required=True, description='List of History Atomics')
