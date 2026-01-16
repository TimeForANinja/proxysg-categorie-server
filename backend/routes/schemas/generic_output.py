from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import OneOf

from db.util.schema import desc


# TODO: make sure output is defined for all routes
class GenericOutput(Schema):
    """Every Output Schema should inherit from this class."""
    status: str = String(
        required=True,
        validate=OneOf(['success', 'failed']),
        metadata=desc("Status of the response, e.g., 'success'"),
    )
    message: str = String(
        required=True,
        metadata=desc('Message describing the operation result'),
    )
