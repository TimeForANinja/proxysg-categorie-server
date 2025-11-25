from apiflask import APIBlueprint, APIFlask
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from db.dbmodel.token import MutableToken
from log import log_debug
from routes.schemas.generic_output import GenericOutput
from routes.schemas.token import ListTokenOutput, CreateOrUpdateTokenOutput, ListTokenCategoriesOutput, SetTokenCategoriesInput


def add_token_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Token Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    token_bp = APIBlueprint('token', __name__)

    # Route to fetch all Tokens
    @token_bp.get('/api/token')
    @token_bp.doc(summary='List all Tokens', description='List all Tokens in the database')
    @token_bp.output(ListTokenOutput)
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_tokens():
        tokens = get_db().tokens.get_all_tokens()
        return {
            'status': 'success',
            'message': 'Tokens fetched successfully',
            'data': tokens,
        }

    # Route to update Token name
    @token_bp.put('/api/token/<string:token_id>')
    @token_bp.doc(summary='Update Token name', description='Update the name of a Token')
    @token_bp.input(class_schema(MutableToken)(), location='json', arg_name='mut_tok')
    @token_bp.output(CreateOrUpdateTokenOutput)
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def update_token(token_id: str, mut_tok: MutableToken):
        new_token = get_db().tokens.update_token(auth.current_user, token_id, mut_tok)
        return {
            'status': 'success',
            'message': 'Token updated successfully',
            'data': new_token
        }

    # Route to update Token name
    @token_bp.post('/api/token/<string:token_id>/roll')
    @token_bp.doc(summary='Roll Token value', description='Randomize the value of a Token')
    @token_bp.output(CreateOrUpdateTokenOutput)
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def roll_token(token_id: str):
        new_token = get_db().tokens.roll_token(auth.current_user, token_id)
        return {
            'status': 'success',
            'message': 'Token rolled successfully',
            'data': new_token
        }

    # Route to delete a Token
    @token_bp.delete('/api/token/<string:token_id>')
    @token_bp.doc(summary='Delete a Token', description='Delete a Token using its ID')
    @token_bp.output(GenericOutput)
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def delete_token(token_id: str):
        get_db().tokens.delete_token(auth.current_user, token_id)
        return {
            'status': 'success',
            'message': 'Token deleted successfully'
        }

    # Route to create a new Token
    @token_bp.post('/api/token')
    @token_bp.doc(summary='Create a Token', description='Create a new Token with a given name')
    @token_bp.input(class_schema(MutableToken)(), location='json', arg_name='mut_tok')
    @token_bp.output(CreateOrUpdateTokenOutput)
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def create_token(mut_tok: MutableToken):
        new_token = get_db().tokens.add_token(auth.current_user, mut_tok)
        return {
            'status': 'success',
            'message': 'Token successfully created',
            'data': new_token
        }

    # Route to add a Category to a Token
    @token_bp.post('/api/token/<string:token_id>/category/<string:cat_id>')
    @token_bp.doc(summary='add cat to token', description='Add the provided Category ID to the Token.Category List')
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def add_token_category(token_id: str, cat_id: str):
        get_db().token_categories.add_token_category(auth.current_user, token_id, cat_id)
        return {
            'status': 'success',
            'message': 'Category successfully added to token'
        }

    # Route to delete a Category from a Token
    @token_bp.delete('/api/token/<string:token_id>/category/<string:cat_id>')
    @token_bp.doc(summary='remove cat from token', description='Remove the provided Category ID from the Token.Category List')
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def delete_token_category(token_id: str, cat_id: str):
        get_db().token_categories.delete_token_category(auth.current_user, token_id, cat_id)
        return {
            'status': 'success',
            'message': 'Category successfully removed from token'
        }

    # Route to set Categories to a given List
    @token_bp.post('/api/token/<string:token_id>/category')
    @token_bp.doc(summary='overwrite token categories', description='Set the Categories of a Token to the provided list')
    @token_bp.input(class_schema(SetTokenCategoriesInput)(), location='json', arg_name='set_cats')
    @token_bp.output(ListTokenCategoriesOutput)
    @token_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def set_token_categories(token_id: str, set_cats: SetTokenCategoriesInput):
        get_db().token_categories.set_token_categories(auth.current_user, token_id, set_cats.categories)
        return {
            'status': 'success',
            'message': 'Token Categories successfully updated',
            'data': set_cats.categories,
        }

    app.register_blueprint(token_bp)
