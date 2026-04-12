from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.core import ListBranchesOutput, ListHistoryOutput, list_branches_output_schema, \
    list_history_output_schema
from routes.schemas.generic_output import GenericOutput, generic_output_schema
from routes.types.core import RestBranchInfo


def add_core_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Core Blueprint')
    core_bp = APIBlueprint('Core', __name__)

    @core_bp.post('/api/me/reset-branch')
    @core_bp.doc(summary='Reset a Users Branch', description='Reset a branch to the latest production commit', tags=['Core'])
    @core_bp.output(generic_output_schema)
    def reset_branch() -> GenericOutput:
        db = get_db()
        user = "system" #  TODO: fetch user from request
        db.core.reset_user_branch(user)
        return GenericOutput(
            status='success',
            message=f'Branch for {user} reset successfully',
        )

    @core_bp.get('/api/branch')
    @core_bp.doc(summary='List all Branches', description='Fetch a list of all available branches', tags=['Core'])
    @core_bp.output(list_branches_output_schema)
    def get_branches() -> ListBranchesOutput:
        db = get_db()
        user = "system" #  TODO: fetch user from request
        branches = db.specials.list_branches()
        data = [
            # TODO: build ro/rw based on user
            RestBranchInfo(name=branch, permission="ro")
            for branch in branches
        ]
        return ListBranchesOutput(
            status='success',
            message='Branches fetched successfully',
            data=data,
        )

    @core_bp.get('/api/branch/<branch>/history')
    @core_bp.doc(summary='List commit history', description='Fetch a list of recent commits for a given branch', tags=['Core'])
    @core_bp.output(list_history_output_schema)
    def get_history(branch: str) -> ListHistoryOutput:
        db = get_db()
        commits = db.specials.fetch_commits(branch)
        return ListHistoryOutput(
            status='success',
            message='History fetched successfully',
            data=commits,
        )

    app.register_blueprint(core_bp)
