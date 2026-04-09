from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from model.types.tags import Commit
from model.types.token import Token
from routes.schemas.generic_output import GenericOutput
from routes.schemas.token import ListTokensOutput, TokenOutput, TokenCategoryOutput, token_input_schema, TokenInput


def add_token_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Token Blueprint')
    token_bp = APIBlueprint('Tokens', __name__)


    @token_bp.get('/api/branch/<branch>/token')
    @token_bp.doc(summary='List all Tokens', description='List all Tokens for a given branch', tags=['Tokens'])
    @token_bp.output(ListTokensOutput)
    def get_tokens(branch: str):
        db = get_db()
        commit = Commit.read_branch(db.backend, branch)
        # TODO: add to "special" section of api routes
        tokens = [Token.read(db.backend, h) for h in commit.head.tokens]
        return {
            'status': 'success',
            'message': 'Tokens fetched successfully',
            'data': tokens,
        }

    @token_bp.post('/api/branch/<branch>/token')
    @token_bp.doc(summary='Create a Token', description='Create a new Token for a given branch', tags=['Tokens'])
    @token_bp.input(token_input_schema, location='json', arg_name='token_data')
    @token_bp.output(TokenOutput)
    def create_token(branch: str, token_data: TokenInput):
        db = get_db()
        token = db.tokens.create_token(branch, token_data.description)
        return {
            'status': 'success',
            'message': 'Token created successfully',
            'data': token,
        }

    @token_bp.delete('/api/branch/<branch>/token/<token_id>')
    @token_bp.doc(summary='Delete a Token', description='Delete a Token by ID for a given branch', tags=['Tokens'])
    @token_bp.output(GenericOutput)
    def delete_token(branch: str, token_id: str):
        db = get_db()
        db.tokens.delete_token(branch, token_id)
        return {
            'status': 'success',
            'message': 'Token deleted successfully',
        }


    @token_bp.get('/api/branch/<branch>/token/<token_id>/category')
    @token_bp.doc(summary='List Category of Token', description='List all categories of a specific token for a given branch', tags=['Tokens', 'Categories'])
    @token_bp.output(TokenCategoryOutput)
    def get_token_categories(branch: str, token_id: str):
        db = get_db()
        categories = db.tokens.get_token_categories(branch, token_id)
        return {
            'status': 'success',
            'message': 'Token category mappings fetched successfully',
            'data': categories,
        }

    @token_bp.post('/api/branch/<branch>/token/<token_id>/category/<category_id>')
    @token_bp.doc(summary='Associate Token with Category', description='Add a category to a token', tags=['Tokens', 'Categories'])
    @token_bp.output(TokenOutput)
    def add_token_category(branch: str, token_id: str, category_id: str):
        db = get_db()
        token = db.tokens.add_token_category(branch, token_id, category_id)
        return {
            'status': 'success',
            'message': 'Category added to token successfully',
            'data': token,
        }

    @token_bp.delete('/api/branch/<branch>/token/<token_id>/category/<category_id>')
    @token_bp.doc(summary='Disassociate Token from Category', description='Remove a category from a token', tags=['Tokens', 'Categories'])
    @token_bp.output(GenericOutput)
    def delete_token_category(branch: str, token_id: str, category_id: str):
        db = get_db()
        db.tokens.delete_token_category(branch, token_id, category_id)
        return {
            'status': 'success',
            'message': 'Category removed from token successfully',
        }

    app.register_blueprint(token_bp)
