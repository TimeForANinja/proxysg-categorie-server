from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.history import ListBranchesOutput, ListHistoryOutput
from routes.schemas.branch import BranchQuery

def add_history_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding History Blueprint')
    history_bp = APIBlueprint('history', __name__)

    @history_bp.get('/api/branch')
    @history_bp.doc(summary='List all Branches', description='Fetch a list of all available branches')
    @history_bp.output(ListBranchesOutput)
    def get_branches():
        db = get_db()
        branches = db.specials.list_branches()
        return {
            'status': 'success',
            'message': 'Branches fetched successfully',
            'data': branches,
        }

    @history_bp.get('/api/history')
    @history_bp.doc(summary='List commit history', description='Fetch a list of recent commits for a given branch')
    @history_bp.input(BranchQuery, location='query')
    @history_bp.output(ListHistoryOutput)
    def get_history(query_data):
        branch = query_data.get('branch')
        db = get_db()
        commits = db.specials.fetch_commits(branch)
        return {
            'status': 'success',
            'message': 'History fetched successfully',
            'data': commits,
        }

    app.register_blueprint(history_bp)
