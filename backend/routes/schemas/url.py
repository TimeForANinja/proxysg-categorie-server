from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList
from dataclasses import field, dataclass

from db.util.schema import desc
from db.dbmodel.url import URL, url_schema
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetURLCategoriesInput:
    """Class for input schema for set categories"""
    categories: tList[str] = field(default_factory=list)


set_url_categories_input_schema = class_schema(SetURLCategoriesInput)()


class CreateOrUpdateURLOutput(GenericOutput):
    """Output schema for create/update url"""
    data: URL = Nested(url_schema, required=True, metadata=desc('URL'))


class ListURLOutput(GenericOutput):
    """Output schema for a list of URL"""
    data: tList[URL] = List(Nested(url_schema), required=True, metadata=desc('List of URLs'))


class ListURLCategoriesOutput(GenericOutput):
    """Output schema for listing Categories of a URL"""
    data: tList[str] = List(String, required=True, metadata=desc('List of Categories'))
