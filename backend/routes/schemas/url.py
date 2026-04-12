from dataclasses import dataclass
from apiflask.fields import List, Nested
from typing import List as tList
from marshmallow_dataclass import class_schema

from routes.types.url import RestURLDetail, rest_url_detail_schema
from util.schema import desc, to_field
from routes.schemas.generic_output import GenericOutput


@dataclass
class ListURLOutput(GenericOutput):
    """Output schema for a list of URL mappings"""
    data: tList[RestURLDetail] = to_field(List(
        Nested(rest_url_detail_schema),
        required=True,
        metadata=desc('List of URL Mappings'),
    ))


list_url_output_schema = class_schema(ListURLOutput)
