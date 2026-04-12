from dataclasses import dataclass
from apiflask.fields import String
from apiflask.validators import OneOf
from marshmallow_dataclass import class_schema

from util.schema import desc, to_field


@dataclass
class GenericOutput:
    """Every Output Schema should inherit from this class."""
    status: str = to_field(String(
        required=True,
        validate=OneOf(['success', 'failed']),
        metadata=desc("Status of the response, e.g., 'success'"),
    ))
    message: str = to_field(String(
        required=True,
        metadata=desc('Message describing the operation result'),
    ))

generic_output_schema = class_schema(GenericOutput)()
