from dataclasses import dataclass

from apiflask.fields import List, Nested, String
from typing import List as tList, Optional

from marshmallow_dataclass import class_schema

from util.schema import desc, to_field
from model.types.category import Category, Member, member_schema, category_schema, constraint_schema, Constraint
from routes.schemas.generic_output import GenericOutput

@dataclass
class MemberInput:
    url: str = to_field(String(required=True, metadata=desc('URL of the member')))
    constraint: Optional[Constraint] = to_field(Nested(
        constraint_schema,
        required=False,
        metadata=desc('Constraint for the member')
    ), default=None)

class MemberOutput(GenericOutput):
    """Output schema for a single member"""
    data: Member = Nested(
        member_schema,
        required=True,
        metadata=desc('Member'),
    )

class ListMembersOutput(GenericOutput):
    """Output schema for a list of members"""
    data: tList[Member] = List(
        Nested(member_schema),
        required=True,
        metadata=desc('List of Members'),
    )

@dataclass
class CategoryInput:
    name: str = to_field(String(
        required=True,
        metadata=desc('Name of the category')
    ))

class CategoryOutput(GenericOutput):
    """Output schema for a single category"""
    data: Category = Nested(
        category_schema,
        required=True,
        metadata=desc('Category'),
    )

class ListCategoriesOutput(GenericOutput):
    """Output schema for a list of categories"""
    data: tList[Category] = List(
        Nested(category_schema),
        required=True,
        metadata=desc('List of Categories'),
    )


member_input_schema = class_schema(MemberInput)()
category_input_schema = class_schema(CategoryInput)()
