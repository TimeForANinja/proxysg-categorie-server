from apiflask.fields import Nested, List, String
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema
from dataclasses import dataclass, field
from typing import List as tList

from db.util.schema import desc
from db.dbmodel.task import Task, task_schema
from routes.schemas.generic_output import GenericOutput


class ListTaskOutput(GenericOutput):
    """Class representing a list of tasks"""
    data: tList[Task] = List(
        Nested(task_schema),
        required=True,
        metadata=desc('List of tasks'),
    )


class SingleTaskOutput(GenericOutput):
    """Class representing a single task"""
    data: Task = Nested(
        task_schema,
        required=True,
        metadata=desc('Task details'),
    )


class CreatedTaskOutput(GenericOutput):
    """Class representing a newly created task"""
    data: str = String(
        required=True,
        metadata=desc('ID of the newly created task'),
    )


@dataclass
class ExistingDBInput:
    """Class representing the DB Structure loaded from an existing DB File"""
    categoryDB: str = field(metadata={
        'required': True,
        'validate': Length(min=1),
        **desc('Content of the existing category DB'),
    })
    prefix: str = field(metadata={
        'required': True,
        'validate': Length(min=1),
        **desc('Prefix of the existing category DB'),
    })


@dataclass
class CleanupInput:
    """Class representing the input for the cleanup endpoint"""
    flags: int = field(metadata={
        'required': True,
        **desc('Flags choosing which cleanup tasks to run'),
    })


existing_db_input_schema = class_schema(ExistingDBInput)()
cleanup_input_schema = class_schema(CleanupInput)()