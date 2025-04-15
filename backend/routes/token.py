import uuid
from apiflask import APIBlueprint, APIFlask
from apiflask.fields import List, Nested
from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from typing import List as tList
from dataclasses import field, dataclass

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from db.token import MutableToken, Token
from log import log_debug
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetTokenCategoriesInput:
    """Class for input schema for set categories"""
    categories: tList[str] = field(default_factory=list)

class CreateOrUpdateTokenOutput(GenericOutput):
    """Output schema for create/update token"""
    data: Token = Nested(class_schema(Token)(), required=True, description="Token")

class ListTokenOutput(GenericOutput):
    """Output schema for list of tokens"""
    data: tList[Token] = List(Nested(class_schema(Token)()), required=True, description="List of Tokens")

class ListTokenCategoriesOutput(GenericOutput):
    """Output schema for listing Categories of a Token"""
    data: tList[str] = List(String, required=True, description="List of Categories")


def add_token_bp(app: APIFlask):
    log_debug("ROUTES", "Adding Token Blueprint")
    auth_if = get_auth_if(app)
    token_bp = APIBlueprint('token', __name__)

    # Route to fetch all Tokens
    @token_bp.get('/api/token')
    @token_bp.doc(summary='List all Tokens', description='List all Tokens in the database')
    @token_bp.output(ListTokenOutput)
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RO])
    def get_tokens():
        db_if = get_db()
        tokens = db_if.tokens.get_all_tokens()
        return {
            "status": "success",
            "message": "Tokens fetched successfully",
            "data": tokens,
        }

    # Route to update Token name
    @token_bp.put('/api/token/<string:token_id>')
    @token_bp.doc(summary='Update Token name', description='Update the name of a Token')
    @token_bp.input(class_schema(MutableToken)(), location='json', arg_name="mut_tok")
    @token_bp.output(CreateOrUpdateTokenOutput)
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def update_token(token_id: str, mut_tok: MutableToken):
        db_if = get_db()
        new_token = db_if.tokens.update_token(token_id, mut_tok)
        db_if.history.add_history_event(f"Token {token_id} updated")
        return {
            "status": "success",
            "message": "Token updated successfully",
            "data": new_token
        }

    # Route to update Token name
    @token_bp.post('/api/token/<string:token_id>/roll')
    @token_bp.doc(summary='Roll Token value', description='Randomize the value of a Token')
    @token_bp.output(CreateOrUpdateTokenOutput)
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def roll_token(token_id: str):
        new_token_val = str(uuid.uuid4())

        db_if = get_db()
        new_token = db_if.tokens.roll_token(token_id, new_token_val)
        db_if.history.add_history_event(f"Token {token_id} rolled")
        return {
            "status": "success",
            "message": "Token rolled successfully",
            "data": new_token
        }

    # Route to delete a Token
    @token_bp.delete('/api/token/<string:token_id>')
    @token_bp.doc(summary="Delete a Token", description="Delete a Token using its ID")
    @token_bp.output(GenericOutput)
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def delete_token(token_id: str):
        db_if = get_db()
        db_if.tokens.delete_token(token_id)
        db_if.history.add_history_event(f"Token {token_id} deleted")
        return {
            "status": "success",
            "message": "Token deleted successfully"
        }

    # Route to create a new Token
    @token_bp.post('/api/token')
    @token_bp.doc(summary="Create a Token", description="Create a new Token with a given name")
    @token_bp.input(class_schema(MutableToken)(), location='json', arg_name="mut_tok")
    @token_bp.output(CreateOrUpdateTokenOutput)
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
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
    @token_bp.post('/api/token/<string:token_id>/category/<string:cat_id>')
    @token_bp.doc(summary="add cat to token", description="Add the provided Category ID to the Token.Category List")
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def add_token_category(token_id: str, cat_id: str):
        db_if = get_db()
        db_if.token_categories.add_token_category(token_id, cat_id)
        db_if.history.add_history_event(f"Added cat {cat_id} to token {token_id}")
        return {
            "status": "success",
            "message": "Category successfully added to token"
        }

    # Route to delete a Category from a Token
    @token_bp.delete('/api/token/<string:token_id>/category/<string:cat_id>')
    @token_bp.doc(summary="remove cat from token", description="Remove the provided Category ID from the Token.Category List")
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def delete_token_category(token_id: str, cat_id: str):
        db_if = get_db()
        db_if.token_categories.delete_token_category(token_id, cat_id)
        db_if.history.add_history_event(f"Removed cat {cat_id} from token {token_id}")
        return {
            "status": "success",
            "message": "Category successfully removed from token"
        }

    # Route to set Categories to a given List
    @token_bp.post('/api/token/<string:token_id>/category')
    @token_bp.doc(summary="overwrite token categories", description="Set the Categories of a Token to the provided list")
    @token_bp.input(class_schema(SetTokenCategoriesInput)(), location='json', arg_name="set_cats")
    @token_bp.output(ListTokenCategoriesOutput)
    @token_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def set_token_categories(token_id: str, set_cats: SetTokenCategoriesInput):
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

    app.register_blueprint(token_bp)
