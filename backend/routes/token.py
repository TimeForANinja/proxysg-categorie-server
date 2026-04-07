from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from model.types.tags import Commit
from model.types.token import Token
from routes.schemas.token import ListTokensOutput
from routes.schemas.branch import BranchQuery

def add_token_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Token Blueprint')
    token_bp = APIBlueprint('tokens', __name__)

    @token_bp.get('/api/token')
    @token_bp.doc(summary='List all Tokens', description='List all Tokens for a given branch')
    @token_bp.input(BranchQuery, location='query')
    @token_bp.output(ListTokensOutput)
    def get_tokens(query_data):
        branch = query_data.get('branch')
        db = get_db()
        commit = Commit.read_branch(db.backend, branch)
        # TODO: add to "special" section of api routes
        tokens = [Token.read(db.backend, h) for h in commit.head.tokens]
        return {
            'status': 'success',
            'message': 'Tokens fetched successfully',
            'data': tokens,
        }

    app.register_blueprint(token_bp)
