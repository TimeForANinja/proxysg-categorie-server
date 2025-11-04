from dataclasses import field, dataclass
from typing import List
from marshmallow.validate import Length

from db.util.validators import simpleURLValidator, simpleStringValidator


# Default Value set in the bc_cats array
# It indicates that a URL has never been queried against the BC Database
NO_BC_CATEGORY_YET = 'to be queried'
# Value returned by BC if the Category-Service is not working
FAILED_BC_CATEGORY_LOOKUP = 'unavailable'


@dataclass(kw_only=True)
class MutableURL:
    hostname: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=4),
            simpleURLValidator,
        ],
        'description': 'FQDN of the URL',
    })
    description: str = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the token'
        },
    )

@dataclass(kw_only=True)
class URL(MutableURL):
    """
    Helper class to represent a URL.
    """
    id: str = field(metadata={
        'required': True,
        'description': 'ID of the URL',
    })
    hostname: str = field(metadata={
        'required': True,
        'validate': [
            Length(min=4),
            simpleURLValidator,
        ],
        'description': 'FQDN of the URL',
    })
    description: str = field(
        default=None,
        metadata={
            'validate': [
                Length(max=255),
                simpleStringValidator,
            ],
            'description': 'Description of the token'
        },
    )
    is_deleted: int = field(
        default=0,
        metadata={
            'description': 'Whether the url is deleted or not',
        }
    )
    categories: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of category IDs associated with the URL',
        }
    )
    bc_cats: List[str] = field(
        default_factory=list,
        metadata={
            'description': 'List of BlueCoat Categories this URL is currently categorised as',
        }
    )
    pending_changes: bool = field(metadata={
        'required': True,
        'description': 'Whether the category has pending changes or not',
    })

    @staticmethod
    def from_mutable(url_id: str, mut_url: MutableURL) -> 'URL':
        return URL(
            hostname=mut_url.hostname,
            description=mut_url.description,
            id=url_id,
            is_deleted=0,
            bc_cats=[NO_BC_CATEGORY_YET],
            pending_changes=False,
        )
