import uuid

from apiflask import APIBlueprint
from marshmallow.fields import Integer

from db.db_singleton import get_db
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList
from dataclasses import field, dataclass


from db.tokens import MutableToken, Token
from routes.schemas.generic_output import GenericOutput

tokens_bp = APIBlueprint('api-tokens', __name__)


@dataclass
class SetCategoriesInput:
    """Class for input schema for set categories"""
    categories: tList[int] = field(default_factory=list)

class CreateOrUpdateOutput(GenericOutput):
    """Output schema for create/update token"""
    data = Nested(class_schema(Token)(), required=True, description="Token")

class ListResponseOutput(GenericOutput):
    """Output schema for list of tokens"""
    data = List(Nested(class_schema(Token)()), required=True, description="List of Tokens")

class ListCategoriesOutput(GenericOutput):
    """Output schema for listing Categories of a Token"""
    data = List(Integer, required=True, description="List of Categories")


# Route to fetch all Tokens
@tokens_bp.get('/api/api-tokens')
@tokens_bp.doc(summary='List all Tokens', description='List all Tokens in the database')
@tokens_bp.output(ListResponseOutput)
def get_tokens():
    db_if = get_db()
    tokens = db_if.tokens.get_all_tokens()
    return {
        "status": "success",
        "message": "Tokens fetched successfully",
        "data": tokens,
    }


# Route to update Token name
@tokens_bp.put('/api/api-tokens/<int:token_id>')
@tokens_bp.doc(summary='Update Token name', description='Update the name of a Token')
@tokens_bp.input(class_schema(MutableToken)(), location='json', arg_name="mut_tok")
@tokens_bp.output(CreateOrUpdateOutput)
def update_token(token_id: int, mut_tok: MutableToken):
    db_if = get_db()
    new_token = db_if.tokens.update_token(token_id, mut_tok)
    db_if.history.add_history_event(f"Token {token_id} updated")
    return {
        "status": "success",
        "message": "Token updated successfully",
        "data": new_token
    }

# Route to update Token name
@tokens_bp.post('/api/api-tokens/<int:token_id>/roll')
@tokens_bp.doc(summary='Roll Token value', description='Randomize the value of a Token')
@tokens_bp.output(CreateOrUpdateOutput)
def roll_token(token_id: int):
    new_token = str(uuid.uuid4())

    db_if = get_db()
    new_token = db_if.tokens.roll_token(token_id, new_token)
    db_if.history.add_history_event(f"Token {token_id} rolled")
    return {
        "status": "success",
        "message": "Token rolled successfully",
        "data": new_token
    }


# Route to delete a Token
@tokens_bp.delete('/api/api-tokens/<int:token_id>')
@tokens_bp.doc(summary="Delete a Token", description="Delete a Token using its ID")
@tokens_bp.output(GenericOutput)
def delete_token(token_id: int):
    db_if = get_db()
    db_if.tokens.delete_token(token_id)
    db_if.history.add_history_event(f"Token {token_id} deleted")
    return {
        "status": "success",
        "message": "Token deleted successfully"
    }


# Route to create a new Token
@tokens_bp.post('/api/api-tokens')
@tokens_bp.doc(summary="Create a Token", description="Create a new Token with a given name")
@tokens_bp.input(class_schema(MutableToken)(), location='json', arg_name="mut_tok")
@tokens_bp.output(CreateOrUpdateOutput)
def create_token(mut_tok: MutableToken):
    new_token = str(uuid.uuid4())

    db_if = get_db()
    new_token = db_if.tokens.add_token(new_token, mut_tok)
    db_if.history.add_history_event(f"Token {new_token.id} created")

    return {
        "status": "success",
        "message": "Token successfully created",
        "data": new_token
    }


# Route to add a Category to a Token
@tokens_bp.post('/api/api-tokens/<int:token_id>/category/<int:cat_id>')
@tokens_bp.doc(summary="add cat to token", description="Add the provided Category ID to the Token.Category List")
def add_token_category(token_id: int, cat_id: int):
    db_if = get_db()
    db_if.token_categories.add_token_category(token_id, cat_id)
    db_if.history.add_history_event(f"Added cat {cat_id} to token {token_id}")
    return {
        "status": "success",
        "message": "Category successfully added to token"
    }


# Route to delete a Category from a Token
@tokens_bp.delete('/api/api-tokens/<int:token_id>/category/<int:cat_id>')
@tokens_bp.doc(summary="remove cat from token", description="Remove the provided Category ID from the Token.Category List")
def delete_token_category(token_id: int, cat_id: int):
    db_if = get_db()
    db_if.token_categories.delete_token_category(token_id, cat_id)
    db_if.history.add_history_event(f"Removed cat {cat_id} from token {token_id} deleted")
    return {
        "status": "success",
        "message": "Category successfully removed from token"
    }


# Route to set Categories to a given List
@tokens_bp.post('/api/api-tokens/<int:token_id>/categories')
@tokens_bp.doc(summary="overwrite token categories", description="Set the Categories of a Token to the provided list")
@tokens_bp.input(class_schema(SetCategoriesInput)(), location='json', arg_name="set_cats")
@tokens_bp.output(ListCategoriesOutput)
def set_token_categories(token_id: int, set_cats: SetCategoriesInput):
    db_if = get_db()
    is_cats = db_if.token_categories.get_token_categories_by_token(token_id)

    added = list(set(set_cats.categories) - set(is_cats))
    removed = list(set(is_cats) - set(set_cats.categories))

    for cat in added:
        db_if.token_categories.add_token_category(token_id, cat)
    for cat in removed:
        db_if.token_categories.delete_token_category(token_id, cat)

    db_if.history.add_history_event(
        f"Updated Cats for Token {token_id} from {','.join([str(c) for c in is_cats])} to {','.join([str(c) for c in set_cats.categories])}")
    return {
        "status": "success",
        "message": "Token Categories successfully updated",
        "data": set_cats.categories,
    }
