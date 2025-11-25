from apiflask.fields import List, Nested
from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from typing import List as tList
from dataclasses import field, dataclass

from db.dbmodel.url import URL
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetURLCategoriesInput:
    """Class for input schema for set categories"""
    categories: tList[str] = field(default_factory=list)


class CreateOrUpdateURLOutput(GenericOutput):
    """Output schema for create/update url"""
    data: URL = Nested(class_schema(URL)(), required=True, description='URL')


class ListURLOutput(GenericOutput):
    """Output schema for a list of URL"""
    data: tList[URL] = List(Nested(class_schema(URL)()), required=True, description='List of URLs')


class ListURLCategoriesOutput(GenericOutput):
    """Output schema for listing Categories of a URL"""
    data: tList[str] = List(String, required=True, description='List of Categories')
