from apiflask.fields import Nested, List, String
from marshmallow_dataclass import class_schema
from typing import List as tList

from db.abc.task import RESTTask
from routes.schemas.generic_output import GenericOutput


class ListTaskOutput(GenericOutput):
    """Class representing a list of tasks"""
    data: tList[RESTTask] = List(
        Nested(class_schema(RESTTask)()),
        required=True,
        description='List of tasks',
    )


class SingleTaskOutput(GenericOutput):
    """Class representing a single task"""
    data: RESTTask = Nested(
        class_schema(RESTTask)(),
        required=True,
        description='Task details',
    )


class CreatedTaskOutput(GenericOutput):
    """Class representing a newly created task"""
    data: str = String(
        required=True,
        description='ID of the newly created task',
    )
