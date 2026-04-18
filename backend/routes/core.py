from typing import cast

from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from model.util.error import ModelError
from model.util.parse_localdb import parse_db
from util.log import log_debug
from model.special import ERROR_NOT_FOUND
from routes.schemas.core import ListBranchesOutput, ListHistoryOutput, list_branches_output_schema, \
    list_history_output_schema, history_input_schema, HistoryInput, CommitInput, commit_input_schema, CommitOutput, \
    commit_output_schema, existing_db_input_schema, ExistingDBInput
from routes.schemas.error import ErrorResponse, OutCanError
from routes.schemas.generic_output import GenericOutput, generic_output_schema
from routes.types.core import RestBranchInfo


def add_core_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Core Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    core_bp = APIBlueprint('Core', __name__)


    @core_bp.get('/api/branch')
    @core_bp.doc(summary='List all Branches', description='Fetch a list of all available branches', tags=['Core'])
    @core_bp.output(list_branches_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_branches() -> ListBranchesOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        branches = db.specials.list_branches()
        data = [
            RestBranchInfo(name=branch, permission=user.get_permission(branch))
            for branch in branches
        ]

        return ListBranchesOutput(
            status='success',
            message='Branches fetched successfully',
            data=data,
        )


    @core_bp.post('/api/branch/@me/reset')
    @core_bp.doc(summary='Reset a Users Branch', description='Reset a branch to the latest production commit', tags=['Core'])
    @core_bp.output(generic_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RW])
    def reset_branch() -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        db.core.reset_user_branch(user)

        return GenericOutput(
            status='success',
            message=f'Branch for {user.username} reset successfully',
        )

    @core_bp.get('/api/branch/<branch>/history')
    @core_bp.doc(summary='List commit history', description='Fetch a list of recent commits for a given branch', tags=['Core'])
    @core_bp.output(list_history_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RO])
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
    @core_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_history_filter(branch: str, history_filter_data: HistoryInput) -> ListHistoryOutput:
        db = get_db()
        commits = db.specials.fetch_commits(branch, history_filter_data.filter_uuid)
        return ListHistoryOutput(
            status='success',
            message='History fetched successfully',
            data=commits,
        )

    @core_bp.post('/api/branch/@me/commit')
    @core_bp.doc(summary='Commit Branch', description='Commit current User-Branch to Prod', tags=['Core'])
    @core_bp.input(commit_input_schema, location='json', arg_name='input_data')
    @core_bp.output(commit_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RW])
    def do_commit(input_data: CommitInput) -> OutCanError[CommitOutput]:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        commit, error = db.core.commit(user, input_data.message)

        if error:
            return ErrorResponse(error)
        return CommitOutput(
            status='success',
            message='Successfully committed to production',
            data=commit,
        )

    @core_bp.post('/api/branch/@me/import')
    @core_bp.doc(summary='Import Local DB', description='Import local database into User-Branch', tags=['Core'])
    @core_bp.input(existing_db_input_schema, location='json', arg_name='existing_db')
    @core_bp.output(generic_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RW])
    def do_import(existing_db: ExistingDBInput) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        try:
            categories = parse_db(existing_db.category_db)
        except Exception as e:
            return ErrorResponse(ModelError(str(e)))

        # apply prefix
        for category in categories:
            category.name = existing_db.prefix + category.name

        # insert to db
        db = get_db()
        db.core.batch_import(user.get_branch(), categories)

        return GenericOutput(
            status='success',
            message='Successfully imported local database',
        )


    @core_bp.get('/api/compile/<string:token_uuid>')
    @core_bp.doc(summary='Compile Categories', description='Compile Categories for the provided Token')
    @core_bp.output(generic_output_schema)
    def handle_compile(token_uuid: str):
        db_if = get_db()
        content, error = db_if.specials.compile_categories(token_uuid)
        if error == ERROR_NOT_FOUND:
            return (
                'Token not found',
                404,
                {'Content-Type': 'text/plain'},
            )

        if error:
            return (
                'Error during compilation',
                500,
                {'Content-Type': 'text/plain'},
            )

        return (
            content,
            200,
            {'Content-Type': 'text/plain'},
        )

    app.register_blueprint(core_bp)
