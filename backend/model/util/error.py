from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass
class ModelError:
    message: str


# a custom type to make our Code more readable
type CanError[T] = tuple[T, None] | tuple[None, ModelError]
