from apiflask.fields import Nested, List, String, Integer
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema
from dataclasses import dataclass
from typing import List as tList

from db.dbmodel.task import Task
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


@dataclass
class CleanupInput:
    """Class representing the input for the cleanup endpoint"""
    flags: int = Integer(
        required=True,
        metadata={'description': 'Flags choosing which cleanup tasks to run'},
    )