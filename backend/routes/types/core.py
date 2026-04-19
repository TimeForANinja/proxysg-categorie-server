from dataclasses import dataclass
from typing import Optional
from apiflask.fields import Integer, String
from marshmallow.validate import OneOf
from marshmallow_dataclass import class_schema

from util.branch_names import BranchPermissionFlag
from util.schema import desc, to_field


@dataclass
class RestCommit:
    uuid: str = to_field(String(required=True, metadata=desc("UUID of the commit")))
    author: str = to_field(String(required=True, metadata=desc("Username of the author")))
    description: str = to_field(String(required=True, metadata=desc("Description of the commit")))
    created_at: int = to_field(Integer(required=True, metadata=desc("Creation timestamp")))
    parent_commit: Optional[str] = to_field(String(
        required=False,
        metadata=desc("UUID of the parent commit, or None if it is the root commit"),
    ), default=None)


@dataclass
class RestBranchInfo:
    name: str = to_field(String(required=True, metadata=desc("Name of the Branch")))
    permission: str = to_field(String(
        required=True,
        validate=OneOf([BranchPermissionFlag.READ_ONLY, BranchPermissionFlag.READ_WRITE]),
        metadata=desc("Permission for the Branch (ro/rw)")
    ))


rest_commit_schema = class_schema(RestCommit)()
rest_branch_info_schema = class_schema(RestBranchInfo)()
