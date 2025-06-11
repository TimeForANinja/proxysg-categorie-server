from apiflask.fields import Nested, List
from dataclasses import dataclass
from marshmallow_dataclass import class_schema
from typing import List as tList

from db.task import Task
from routes.schemas.generic_output import GenericOutput


@dataclass
class ListTaskOutput(GenericOutput):
    """Class representing a list of tasks"""
    data: tList[Task] = List(
        Nested(class_schema(Task)()),
        required=True,
        description='List of tasks',
    )
