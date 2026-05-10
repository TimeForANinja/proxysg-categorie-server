from dataclasses import dataclass

from model.util.error import ModelError
from routes.schemas.generic_output import GenericOutput


type OutCanError[T] = T | ErrorResponse


@dataclass
class ErrorResponse(GenericOutput):
    def __init__(self, error: ModelError):
        self.status = "failed"
        self.message = error.message
