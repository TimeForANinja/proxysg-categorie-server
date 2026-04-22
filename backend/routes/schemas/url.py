from dataclasses import dataclass
from apiflask.fields import List, Nested, String, Boolean
from typing import List as tList
from marshmallow_dataclass import class_schema

from routes.types.url import RestURLDetail, rest_url_detail_schema, rest_test_result_schema
from util.schema import desc, to_field
from routes.schemas.generic_output import GenericOutput
from model.types.url import URL, url_schema


@dataclass
class ListUrlsQuery:
    add_mappings: bool = to_field(Boolean(
        load_default=False,
        metadata=desc("pad with Category mappings"),
    ), default=False)
    add_bc_cat: bool = to_field(Boolean(
        load_default=False,
        metadata=desc("pad with BC Categories"),
    ), default=False)


@dataclass
class URLCreateInput:
    url: str = to_field(String(
        required=True,
        metadata=desc("Value of the URL")
    ))
    description: str = to_field(String(
        required=False,
        metadata=desc("Description of the URL")
    ))


@dataclass
class URLUpdateInput:
    url: str = to_field(String(
        required=False,
        metadata=desc("Value of the URL")
    ))
    description: str = to_field(String(
        required=False,
        metadata=desc("Description of the URL")
    ))


@dataclass
class URLOutput(GenericOutput):
    """Output schema for a single URL"""
    data: URL = to_field(Nested(
        url_schema,
        required=True,
        metadata=desc("URL"),
    ))


@dataclass
class ListURLOutput(GenericOutput):
    """Output schema for a list of URL mappings"""
    data: tList[RestURLDetail] = to_field(List(
        Nested(rest_url_detail_schema),
        required=True,
        metadata=desc("List of URL Mappings"),
    ))


@dataclass
class URLTestInput:
    urls: List[str] = to_field(List(
        String(required=True, metadata=desc("Value of the URL to test")),
        required=True,
    ))

@dataclass
class URLTestOutput(GenericOutput):
    """Output schema for a list of URL mappings"""
    data: tList[RestURLDetail] = to_field(List(
        Nested(rest_test_result_schema),
        required=True,
        metadata=desc("List of Test Results"),
    ))


list_urls_query_schema = class_schema(ListUrlsQuery)()
list_url_output_schema = class_schema(ListURLOutput)()
url_create_input_schema = class_schema(URLCreateInput)()
url_update_input_schema = class_schema(URLUpdateInput)()
url_output_schema = class_schema(URLOutput)()
url_test_input_schema = class_schema(URLTestInput)()
url_test_output_schema = class_schema(URLTestOutput)()
