from apiflask.fields import List, Nested, String
from typing import List as tList

from util.schema import desc
from model.types.tags import Commit, commit_schema
from routes.schemas.generic_output import GenericOutput


class ListBranchesOutput(GenericOutput):
    """Output schema for a list of branches"""
    data: tList[str] = List(
        String,
        required=True,
        metadata=desc('List of Branches'),
    )

class ListHistoryOutput(GenericOutput):
    """Output schema for a list of recent commits"""
    data: tList[Commit] = List(
        Nested(commit_schema),
        required=True,
        metadata=desc('List of Commits'),
    )
