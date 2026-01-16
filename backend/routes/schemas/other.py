from apiflask.fields import List, Nested
from marshmallow.fields import String
from typing import List as tList
from apiflask import Schema

from db.util.schema import desc
from db.dbmodel.category import Category, category_schema
from db.dbmodel.url import URL, url_schema
from routes.schemas.generic_output import GenericOutput


class TestReply(Schema):
    input: str = String(
        required=True,
        metadata=desc('(sanitized) input used for tests'),
    )
    matched_url: URL = Nested(
        url_schema,
        required=False,
        metadata=desc('URL that matched (or none)'),
    )
    local_categories: tList[Category] = List(
        Nested(category_schema),
        required=True,
        metadata=desc('List of Categories of the matched URL'),
    )
    bc_categories: tList[str] = List(
        String,
        required=True,
        metadata=desc('List Bluecoat Categories'),
    )


class TestURIOutput(GenericOutput):
    """Output schema for testing a URL against the DBs"""
    data: TestReply = Nested(TestReply, required=True, metadata=desc('Test Reply'))
