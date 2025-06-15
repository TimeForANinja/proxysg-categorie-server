from apiflask.fields import Nested, List, String
from marshmallow_dataclass import class_schema
from typing import List as tList

from db.task import Task
from routes.schemas.generic_output import GenericOutput


class ListTaskOutput(GenericOutput):
    """Class representing a list of tasks"""
    data: tList[Task] = List(
        Nested(class_schema(Task)()),
        required=True,
        description='List of tasks',
    )


class SingleTaskOutput(GenericOutput):
    """Class representing a single task"""
    data: Task = Nested(
        class_schema(Task)(),
        required=True,
        description='Task details',
    )


class CreatedTaskOutput(GenericOutput):
    """Class representing a newly created task"""
    data: str = String(
        required=True,
        description='ID of the newly created task',
    )
