from typing import cast
from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from util.log import log_debug
from routes.schemas.core import ListBranchesOutput, ListHistoryOutput, list_branches_output_schema, \
    history_input_schema, list_history_output_schema, CommitOutput, HistoryInput, commit_output_schema, \
    commit_input_schema, CommitInput, revert_input_schema, RevertInput
from routes.schemas.error import ErrorResponse, OutCanError
from routes.schemas.generic_output import GenericOutput, generic_output_schema
from routes.types.core import RestBranchInfo


def add_core_bp(app: APIFlask):
    log_debug("ROUTES", "Adding Core Blueprint")
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    core_bp = APIBlueprint("Core", __name__)


    @core_bp.get("/api/branch")
    @core_bp.doc(summary="List all Branches", description="Fetch a list of all available branches", tags=["Core"])
    @core_bp.output(list_branches_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_branches() -> ListBranchesOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        branches = db.core.list_branches()
        data = [
            RestBranchInfo(name=branch, permission=user.get_permission(branch))
            for branch in branches
        ]

        return ListBranchesOutput(
            status="success",
            message="Branches fetched successfully",
            data=data,
        )

    @core_bp.post("/api/branch/@me/reset")
    @core_bp.doc(summary="Reset a Users Branch", description="Reset a branch to the latest production commit", tags=["Core"])
    @core_bp.output(generic_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RW])
    def reset_branch() -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        db.core.reset_user_branch(user)

        return GenericOutput(
            status="success",
            message=f"Branch for {user.username} reset successfully",
        )


    @core_bp.post("/api/branch/@me/revert")
    @core_bp.doc(summary="Revert a Users Branch", description="Revert a user-branch to a specific commit state", tags=["Core"])
    @core_bp.input(revert_input_schema, location="json", arg_name="input_data")
    @core_bp.output(generic_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RW])
    def revert_branch(input_data: RevertInput) -> OutCanError[GenericOutput]:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.core.revert(user, input_data.commit_uuid)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message=f"Branch for {user.username} reverted successfully",
        )


    @core_bp.get("/api/branch/<string:branch>/history")
    @core_bp.doc(summary="List commit history", description="Fetch a list of recent commits starting with the given branch", tags=["Core"])
    @core_bp.output(list_history_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_history(branch: str) -> ListHistoryOutput:
        db = get_db()
        commits = db.core.fetch_commits(branch, None)
        return ListHistoryOutput(
            status="success",
            message="History fetched successfully",
            data=commits,
        )

    @core_bp.post("/api/branch/<string:branch>/history")
    @core_bp.doc(summary="List commit history", description="Fetch a list of recent commits starting with the given branch, including filtering for specific uuid involvement", tags=["Core"])
    @core_bp.input(history_input_schema, location="json", arg_name="history_filter_data")
    @core_bp.output(list_history_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_history_filter(branch: str, history_filter_data: HistoryInput) -> ListHistoryOutput:
        db = get_db()
        commits = db.core.fetch_commits(branch, history_filter_data.filter_uuid)
        return ListHistoryOutput(
            status="success",
            message="History fetched successfully",
            data=commits,
        )


    @core_bp.post("/api/branch/@me/commit")
    @core_bp.doc(summary="Commit Branch", description="Commit current User-Branch to Prod", tags=["Core"])
    @core_bp.input(commit_input_schema, location="json", arg_name="input_data")
    @core_bp.output(commit_output_schema)
    @core_bp.auth_required(auth, roles=[AuthRoles.RW])
    def do_commit(input_data: CommitInput) -> OutCanError[CommitOutput]:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        commit, error = db.core.commit(user, input_data.message)

        if error:
            return ErrorResponse(error)
        return CommitOutput(
            status="success",
            message="Successfully committed to production",
            data=commit,
        )

    app.register_blueprint(core_bp)
