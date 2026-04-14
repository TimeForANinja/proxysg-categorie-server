from dataclasses import dataclass
from typing import Optional, List as tList
from marshmallow.fields import Integer, List, String
from marshmallow.validate import OneOf

from marshmallow_dataclass import class_schema
from util.schema import desc, to_field


@dataclass
class RestStateRootTreeRootNode:
    categories: tList[str] = to_field(List(
        String(required=True, metadata=desc('Category ID')),
        required=True,
        metadata=desc('List of all Categories in this Version'),
    ))
    tokens: tList[str] = to_field(List(
        String(required=True, metadata=desc('Token ID')),
        required=True,
        metadata=desc('List of all Tokens in this Version'),
    ))
    urls: tList[str] = to_field(List(
        String(required=True, metadata=desc('URL ID')),
        required=True,
        metadata=desc('List of all URLs in this Version'),
    ))
    url_category_mappings: tList[str] = to_field(List(
        String(required=True, metadata=desc('Mapping ID')),
        required=True,
        metadata=desc('List of all URL-Category Mappings in this Version'),
    ))
    token_category_mappings: tList[str] = to_field(List(
        String(required=True, metadata=desc('Mapping ID')),
        required=True,
        metadata=desc('List of all Token-Category Mappings in this Version'),
    ))


@dataclass
class RestCommit:
    uuid: str = to_field(String(required=True, metadata=desc('UUID of the commit')))
    author: str = to_field(String(required=True, metadata=desc('Username of the author')))
    description: str = to_field(String(required=True, metadata=desc('Description of the commit')))
    created_at: int = to_field(Integer(required=True, metadata=desc('Creation timestamp')))
    parent_commit: Optional[str] = to_field(String(
        required=False,
        metadata=desc('UUID of the parent commit, or None if it is the root commit'),
    ), default=None)


@dataclass
class RestBranchInfo:
    name: str = to_field(String(
        required=True,
        validate=OneOf(['ro', 'rw']),
        metadata=desc('Name of the Branch')
    ))
    permission: str = to_field(String(required=True, metadata=desc('Permission for the Branch (ro/rw)')))


rest_commit_schema = class_schema(RestCommit)()
rest_branch_info_schema = class_schema(RestBranchInfo)()
