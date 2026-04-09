from apiflask.fields import List, Nested
from typing import List as tList

from model.types.url import url_mapping_schema
from util.schema import desc
from model.special import URLMapping
from routes.schemas.generic_output import GenericOutput


class ListURLOutput(GenericOutput):
    """Output schema for a list of URL mappings"""
    data: tList[URLMapping] = List(
        Nested(url_mapping_schema),
        required=True,
        metadata=desc('List of URL Mappings'),
    )
