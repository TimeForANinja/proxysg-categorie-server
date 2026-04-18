from dataclasses import dataclass


@dataclass
class ModelError:
    message: str


# a custom type to make our Code more readable
type CanError[T] = tuple[T, None] | tuple[None, ModelError]
