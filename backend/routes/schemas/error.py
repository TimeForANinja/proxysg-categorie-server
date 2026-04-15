from dataclasses import dataclass

from model.types.error import ModelError
from routes.schemas.generic_output import GenericOutput


type OutCanError[T] = T | ErrorResponse


@dataclass
class ErrorResponse(GenericOutput):
    def __init__(self, error: ModelError):
        self.message = error.message
        self.status = "failed"
