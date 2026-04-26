from dataclasses import dataclass
from datetime import datetime
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

    def parse_range(self) -> str:
        if self.start < 0 and self.end < 0:
            return "N/A"

        start_date_str = "..."
        if self.start >= 0:
            start_date_str = datetime.fromtimestamp(self.start).strftime("%Y-%m-%d")

        end_date_str = "..."
        if self.end >= 0:
            end_date_str = datetime.fromtimestamp(self.end).strftime("%Y-%m-%d")

        return f"{start_date_str} - {end_date_str}"


constraint_schema = class_schema(Constraint)()
