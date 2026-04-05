from dataclasses import field, dataclass
from typing import List, Dict, Any
from marshmallow.validate import Length
from marshmallow_dataclass import class_schema

from db.util.validators import simpleURLValidator, simpleStringValidator
from db.util.schema import desc


@dataclass(kw_only=True)
class MutableURL:
    hostname: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=4),
            simpleURLValidator,
        ],
        **desc('FQDN of the URL'),
    })
    description: str = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            **desc('Description of the token'),
        },
    )


@dataclass(kw_only=True)
class URL(MutableURL):
    """
    Helper class to represent a URL.
    """
    id: str = field(metadata={
        'required': True,
        **desc('ID of the URL'),
    })
    hostname: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=4),
            simpleURLValidator,
        ],
        **desc('FQDN of the URL'),
    })
    description: str = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            **desc('Description of the token'),
        },
    )
    categories: List[str] = field(
        default_factory=list,
        metadata=desc('List of category IDs associated with the URL'),
    )

    def mutable_dict(self) -> Dict[str, Any]:
        """
        Utility to get a Dict of all mutable fields
        Used with the diff utility to calculate which fields are being changed
        """
        return {
            "hostname": self.hostname,
            "description": self.description,
        }

    @staticmethod
    def from_mutable(url_id: str, mut_url: MutableURL) -> 'URL':
        return URL(
            id=url_id,
            hostname=mut_url.hostname,
            description=mut_url.description,
            categories=[],
        )


mutable_url_schema = class_schema(MutableURL)()
url_schema = class_schema(URL)()
