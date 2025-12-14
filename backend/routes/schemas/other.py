from apiflask.fields import List, Nested
from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from typing import List as tList
from apiflask import Schema

from db.dbmodel.category import Category
from db.dbmodel.url import URL
from routes.schemas.generic_output import GenericOutput


class TestReply(Schema):
    input: str = String(
        required=True,
        description='(sanitized) input used for tests',
    )
    matched_url: URL = Nested(
        class_schema(URL)(),
        required=False,
        description='URL that matched (or none)'
    )
    local_categories: tList[Category] = List(
        Nested(class_schema(Category)()),
        required=True,
        description='List of Categories of the matched URL'
    )
    bc_categories: tList[str] = List(
        String,
        required=True,
        description='List Bluecoat Categories'
    )


class TestURIOutput(GenericOutput):
    """Output schema for testing a URL against the DBs"""
    data: TestReply = Nested(TestReply, required=True, description='Test Reply')
