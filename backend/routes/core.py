from apiflask import APIBlueprint, APIFlask

from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.core import ListBranchesOutput, ListHistoryOutput, list_branches_output_schema, \
    list_history_output_schema, history_input_schema, HistoryInput, CommitInput, commit_input_schema, CommitOutput, \
    commit_output_schema
from routes.schemas.error import ErrorResponse, OutCanError
from routes.schemas.generic_output import GenericOutput, generic_output_schema
from routes.types.core import RestBranchInfo


def add_core_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Core Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    core_bp = APIBlueprint('Core', __name__)

    @core_bp.post('/api/me/reset-branch')
    @core_bp.doc(summary='Reset a Users Branch', description='Reset a branch to the latest production commit', tags=['Core'])
    @core_bp.output(generic_output_schema)
    @core_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def reset_branch() -> GenericOutput:
        db = get_db()
        user: AuthUser = auth.current_user
        db.core.reset_user_branch(user.username)
        return GenericOutput(
            status='success',
            message=f'Branch for {user.username} reset successfully',
        )

    @core_bp.get('/api/branch')
    @core_bp.doc(summary='List all Branches', description='Fetch a list of all available branches', tags=['Core'])
    @core_bp.output(list_branches_output_schema)
    @core_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_branches() -> ListBranchesOutput:
        db = get_db()
        user: AuthUser = auth.current_user
        branches = db.specials.list_branches()
        data = [
            RestBranchInfo(name=branch, permission=RestBranchInfo.get_permission(branch, user))
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
    @core_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_history(branch: str) -> ListHistoryOutput:
        db = get_db()
        commits = db.specials.fetch_commits(branch, None)
        return ListHistoryOutput(
            status='success',
            message='History fetched successfully',
            data=commits,
        )

    @core_bp.post('/api/branch/<branch>/history')
    @core_bp.doc(summary='List commit history', description='Fetch a list of recent commits for a given branch, including filtering for specific uuid involvement', tags=['Core'])
    @core_bp.input(history_input_schema, location='json', arg_name='history_filter_data')
    @core_bp.output(list_history_output_schema)
    @core_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_history_filter(branch: str, history_filter_data: HistoryInput) -> ListHistoryOutput:
        db = get_db()
        commits = db.specials.fetch_commits(branch, history_filter_data.filter_uuid)
        return ListHistoryOutput(
            status='success',
            message='History fetched successfully',
            data=commits,
        )

    @core_bp.post('/api/me/commit')
    @core_bp.doc(summary='Commit ', description='Commit current User-Branch to Prod', tags=['Core'])
    @core_bp.input(commit_input_schema, location='json', arg_name='input_data')
    @core_bp.output(commit_output_schema)
    @core_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def do_commit(input_data: CommitInput) -> OutCanError[CommitOutput]:
        user: AuthUser = auth.current_user

        db = get_db()
        commit, error = db.core.commit(user.username, input_data.message)
        if error:
            return ErrorResponse(error)
        return CommitOutput(
            status='success',
            message='Successfully committed to production',
            data=commit,
        )

    app.register_blueprint(core_bp)
