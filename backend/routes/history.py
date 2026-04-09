from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.history import ListBranchesOutput, ListHistoryOutput
from routes.schemas.generic_output import GenericOutput


def add_history_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding History Blueprint')
    history_bp = APIBlueprint('History', __name__)

    @history_bp.post('/api/me/reset-branch')
    @history_bp.doc(summary='Reset a Users Branch', description='Reset a branch to the latest production commit', tags=['History'])
    @history_bp.output(GenericOutput)
    def reset_branch():
        db = get_db()
        user = "system" #  TODO: fetch user from request
        db.tags.reset_user_branch(user)
        return {
            'status': 'success',
            'message': f'Branch for {user} reset successfully',
        }

    @history_bp.get('/api/branch')
    @history_bp.doc(summary='List all Branches', description='Fetch a list of all available branches', tags=['History'])
    @history_bp.output(ListBranchesOutput)
    def get_branches():
        db = get_db()
        branches = db.specials.list_branches()
        return {
            'status': 'success',
            'message': 'Branches fetched successfully',
            'data': branches,
        }

    @history_bp.get('/api/branch/<branch>/history')
    @history_bp.doc(summary='List commit history', description='Fetch a list of recent commits for a given branch', tags=['History'])
    @history_bp.output(ListHistoryOutput)
    def get_history(branch: str):
        db = get_db()
        commits = db.specials.fetch_commits(branch)
        return {
            'status': 'success',
            'message': 'History fetched successfully',
            'data': commits,
        }

    app.register_blueprint(history_bp)
