from dataclasses import dataclass
from apiflask.fields import Dict, String
from typing import Dict as tDict, Any
from marshmallow_dataclass import class_schema

from util.schema import desc, to_field
from routes.schemas.generic_output import GenericOutput


@dataclass
class ExistingDBInput:
    """Class representing the DB Structure loaded from an existing DB File"""
    category_db: str = to_field(String(
        required=True,
        metadata=desc("^Content of the existing category DB"),
    ))
    prefix: str = to_field(String(
        required=True,
        metadata=desc("Prefix of the existing category DB"),
    ))

@dataclass
class ListMetricsOutput(GenericOutput):
    """Output schema for a list of branches"""
    data: tDict[str, Any] = to_field(Dict(
            required=True,
            metadata=desc("Dictionary of Metrics"),
    ))

@dataclass
class Status304Header:
    """Header for a 304 Not Modified response"""
    if_modified_since: str = to_field(String(
        required=False,
        data_key="If-Modified-Since",
        metadata=desc("Value of the If-Modified-Since Header"),
    ), default=None)

@dataclass
class DiffOutput(GenericOutput):
    """Output schema for the diff YAML representations"""
    data: str = to_field(String(
        required=True,
        metadata=desc("YAML representation of the first commit"),
    ))


existing_db_input_schema = class_schema(ExistingDBInput)()
list_metrics_output_schema = class_schema(ListMetricsOutput)()
status304_header_schema = class_schema(Status304Header)()
diff_output_schema = class_schema(DiffOutput)()
