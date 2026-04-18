from dataclasses import dataclass
from apiflask.fields import List, Nested
from typing import List as tList, Optional

from marshmallow.fields import String
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

@dataclass
class HistoryInput:
    filter_uuid: Optional[List[str]] = to_field(List(
        String(required=True, metadata=desc('ID')),
        required=False,
        metadata=desc('List of all UUIDs to filter by relevance for'),
    ), default=None)

@dataclass
class ExistingDBInput:
    """Class representing the DB Structure loaded from an existing DB File"""
    category_db: str = to_field(String(
        required=True,
        metadata=desc('^Content of the existing category DB'),
    ))
    prefix: str = to_field(String(
        required=True,
        metadata=desc('Prefix of the existing category DB'),
    ))

@dataclass
class CommitInput:
    message: str = to_field(String(
        required=True,
        metadata=desc("Commit message"),
    ))

@dataclass
class CommitOutput(GenericOutput):
    """Output schema for a list of recent commits"""
    data: RestCommit = to_field(Nested(
        rest_commit_schema,
        required=True,
        metadata=desc('new Commit'),
    ))

history_input_schema = class_schema(HistoryInput)()
list_branches_output_schema = class_schema(ListBranchesOutput)()
list_history_output_schema = class_schema(ListHistoryOutput)()
existing_db_input_schema = class_schema(ExistingDBInput)()
commit_input_schema = class_schema(CommitInput)()
commit_output_schema = class_schema(CommitOutput)()
