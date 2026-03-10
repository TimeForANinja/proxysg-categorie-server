from dataclasses import field, dataclass
from typing import Optional, Dict, Any
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from db.util.validators import simpleNameValidator, simpleStringValidator
from db.util.schema import desc


@dataclass(kw_only=True)
class MutableCategory:
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        **desc('Name of the category'),
    })
    color: int = field(metadata={
        'required': True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            **desc('Description of the category'),
        },
    )


@dataclass(kw_only=True)
class Category(MutableCategory):
    """
    Helper class to represent a category.
    """
    id: str = field(metadata={
        'required': True,
        **desc('ID of the category'),
    })
    name: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=1),
            simpleNameValidator,
        ],
        **desc('Name of the category'),
    })
    color: int = field(metadata={
        'required': True,
    })
    description: Optional[str] = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            **desc('Description of the category'),
        },
    )

    def mutable_dict(self) -> Dict[str, Any]:
        """
        Utility to get a Dict of all mutable fields
        Used with the diff utility to calculate which fields are being changed
        """
        return {
            "name": self.name,
            "color": self.color,
            "description": self.description,
        }

    @staticmethod
    def from_mutable(category_id: str, mut_category: MutableCategory) -> 'Category':
        return Category(
            id=category_id,
            name=mut_category.name,
            color=mut_category.color,
            description=mut_category.description,
        )


mutable_category_schema = class_schema(MutableCategory)()
category_schema = class_schema(Category)()
