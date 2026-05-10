from dataclasses import dataclass
from typing import Optional, List as tList
from apiflask.fields import String, Nested, List
from marshmallow_dataclass import class_schema

from util.schema import to_field, desc


@dataclass
class AuthUIComponent:
    type: str = to_field(String(
        required=True,
        metadata=desc("Type of UI component (e.g. 'button', 'input-text', ...)"),
    ))
    label: Optional[str] = to_field(String(
        required=False,
        metadata=desc("Label to display on/next to the component"),
    ), default=None)
    location: Optional[str] = to_field(String(
        required=False,
        metadata=desc("Location to redirect to on press"),
    ), default=None)
    key: Optional[str] = to_field(String(
        required=False,
        metadata=desc("Key in which the value will be stored and included in the login post"),
    ), default=None)

auth_ui_component_schema = class_schema(AuthUIComponent)()


@dataclass
class AuthMechanism:
    type: str = to_field(String(
        required=True,
        metadata=desc("(unique) type identified for the  auth mechanism"),
    ))
    label: str = to_field(String(
        required=True,
        metadata=desc("Human-readable label for the auth mechanism"),
    ))
    ui: tList[AuthUIComponent] = to_field(List(
        Nested(auth_ui_component_schema),
        required=True,
        metadata=desc("UI components to display for this mechanism"),
    ))

auth_mechanism_schema = class_schema(AuthMechanism)()
