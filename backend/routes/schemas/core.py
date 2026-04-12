from dataclasses import dataclass
from apiflask.fields import List, Nested
from typing import List as tList
from marshmallow_dataclass import class_schema

from routes.types.core import RestCommit, rest_commit_schema, rest_branch_info_schema, RestBranchInfo
from util.schema import desc, to_field
from routes.schemas.generic_output import GenericOutput


@dataclass
class ListBranchesOutput(GenericOutput):
    """Output schema for a list of branches"""
    data: tList[RestBranchInfo] = to_field(List(
        Nested(rest_branch_info_schema),
        required=True,
        metadata=desc('List of Branches'),
    ))

@dataclass
class ListHistoryOutput(GenericOutput):
    """Output schema for a list of recent commits"""
    data: tList[RestCommit] = to_field(List(
        Nested(rest_commit_schema),
        required=True,
        metadata=desc('List of Commits'),
    ))


list_branches_output_schema = class_schema(ListBranchesOutput)()
list_history_output_schema = class_schema(ListHistoryOutput)()
