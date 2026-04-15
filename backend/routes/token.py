from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.category import ListCategoryOutput, list_category_output_schema
from routes.schemas.error import OutCanError, ErrorResponse
from routes.schemas.generic_output import GenericOutput, generic_output_schema
from routes.schemas.token import ListTokenOutput, TokenOutput, token_input_schema, TokenInput, \
    TokenCategoryMappingInput, token_category_mapping_input_schema, list_token_output_schema, token_output_schema


def add_token_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Token Blueprint')
    token_bp = APIBlueprint('Tokens', __name__)


    @token_bp.get('/api/branch/<branch>/token')
    @token_bp.doc(summary='List all Tokens', description='List all Tokens for a given branch', tags=['Tokens'])
    @token_bp.output(list_token_output_schema)
    def get_tokens(branch: str) -> ListTokenOutput:
        db = get_db()
        tokens = db.specials.fetch_tokens(branch)
        return ListTokenOutput(
            status='success',
            message='Tokens fetched successfully',
            data=tokens,
        )

    @token_bp.post('/api/branch/<branch>/token')
    @token_bp.doc(summary='Create a Token', description='Create a new Token for a given branch', tags=['Tokens'])
    @token_bp.input(token_input_schema, location='json', arg_name='token_data')
    @token_bp.output(token_output_schema)
    def create_token(branch: str, token_data: TokenInput) -> TokenOutput:
        db = get_db()
        token = db.tokens.create_token(branch, token_data.description)
        return TokenOutput(
            status='success',
            message='Token created successfully',
            data=token,
        )

    @token_bp.put('/api/branch/<branch>/token/<token_id>')
    @token_bp.doc(summary='Update a Token', description='Update a Token by ID for a given branch', tags=['Tokens'])
    @token_bp.input(token_input_schema, location='json', arg_name='token_data')
    @token_bp.output(token_output_schema)
    def update_token(branch: str, token_id: str, token_data: TokenInput) -> OutCanError[TokenOutput]:
        db = get_db()
        token, error = db.tokens.update_token(branch, token_id, token_data.description)
        if error:
            return ErrorResponse(error)
        return TokenOutput(
            status='success',
            message='Token updated successfully',
            data=token,
        )

    @token_bp.delete('/api/branch/<branch>/token/<token_id>')
    @token_bp.doc(summary='Delete a Token', description='Delete a Token by ID for a given branch', tags=['Tokens'])
    @token_bp.output(generic_output_schema)
    def delete_token(branch: str, token_id: str) -> GenericOutput:
        db = get_db()
        error = db.tokens.delete_token(branch, token_id)
        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='Token deleted successfully',
        )

    @token_bp.post('/api/branch/<branch>/token/<token_id>/roll')
    @token_bp.doc(summary='Roll Token Value', description='Generate a new secret for a specific token', tags=['Tokens'])
    @token_bp.output(token_output_schema)
    def roll_token(branch: str, token_id: str) -> OutCanError[TokenOutput]:
        db = get_db()
        token, error = db.tokens.roll_token(branch, token_id)
        if error:
            return ErrorResponse(error)
        return TokenOutput(
            status='success',
            message='Token rolled successfully',
            data=token,
        )


    @token_bp.get('/api/branch/<branch>/token/<token_id>/category')
    @token_bp.doc(summary='List all Category of Token', description='List all categories of a specific token for a given branch', tags=['Tokens', 'Categories', 'Mapping'])
    @token_bp.output(list_category_output_schema)
    def get_token_categories(branch: str, token_id: str) -> ListCategoryOutput:
        db = get_db()
        categories = db.mappings.get_token_categories(branch, token_id)
        return ListCategoryOutput(
            status='success',
            message='Token category mappings fetched successfully',
            data=categories,
        )

    @token_bp.post('/api/branch/<branch>/token/<token_id>/category')
    @token_bp.doc(summary='Associate Token with Category', description='Add a category to a token', tags=['Tokens', 'Categories', 'Mapping'])
    @token_bp.input(token_category_mapping_input_schema, location='json', arg_name='mapping_data')
    @token_bp.output(generic_output_schema)
    def add_token_category(branch: str, token_id: str, mapping_data: TokenCategoryMappingInput) -> GenericOutput:
        db = get_db()
        error = db.mappings.add_token_category(branch, token_id, mapping_data.category_id)
        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='Category added to token successfully',
        )

    @token_bp.delete('/api/branch/<branch>/token/<token_id>/category/<category_id>')
    @token_bp.doc(summary='Disassociate Token from Category', description='Remove a category from a token', tags=['Tokens', 'Categories', 'Mapping'])
    @token_bp.output(generic_output_schema)
    def delete_token_category(branch: str, token_id: str, category_id: str) -> GenericOutput:
        db = get_db()
        error = db.mappings.delete_token_category(branch, token_id, category_id)
        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='Category removed from token successfully',
        )

    app.register_blueprint(token_bp)
