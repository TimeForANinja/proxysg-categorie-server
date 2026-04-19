from dataclasses import dataclass
from typing import Dict, Any
from marshmallow.fields import String, Integer
from marshmallow_dataclass import class_schema

from util.schema import desc, to_field


@dataclass
class Constraint:
    start: int = to_field(Integer(required=True, metadata=desc("Unix timestamp from, -1 for no limit")))
    end: int = to_field(Integer(required=True, metadata=desc("Unix timestamp until, -1 for no limit")))
    comment: str = to_field(String(required=True, metadata=desc("Comment for the constraint")))

    def serialize(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "comment": self.comment,
        }

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> 'Constraint':
        return Constraint(
            start=data["start"],
            end=data["end"],
            comment=data["comment"],
        )


constraint_schema = class_schema(Constraint)()
