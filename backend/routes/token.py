from typing import cast
from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from util.log import log_debug
from routes.schemas.error import OutCanError, ErrorResponse
from routes.schemas.generic_output import GenericOutput, generic_output_schema
from routes.schemas.token import ListTokenOutput, TokenOutput, token_create_input_schema, token_update_input_schema, \
    TokenCreateInput, TokenUpdateInput, list_token_output_schema, token_output_schema, list_tokens_query_schema, \
    ListTokensQuery


def add_token_bp(app: APIFlask):
    log_debug("ROUTES", "Adding Token Blueprint")
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    token_bp = APIBlueprint("Tokens", __name__)


    @token_bp.get("/api/branch/<string:branch>/token")
    @token_bp.doc(summary="List all Tokens", description="List all Tokens for a given branch", tags=["Tokens"])
    @token_bp.input(list_tokens_query_schema, location="query", arg_name="flags")
    @token_bp.output(list_token_output_schema)
    @token_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_tokens(branch: str, flags: ListTokensQuery) -> ListTokenOutput:
        db = get_db()
        tokens = db.tokens.fetch_tokens(branch, flags.add_mappings, flags.add_last_used)
        return ListTokenOutput(
            status="success",
            message="Tokens fetched successfully",
            data=tokens,
        )

    @token_bp.post("/api/branch/@me/token")
    @token_bp.doc(summary="Create a Token", description="Create a new Token for a given branch", tags=["Tokens"])
    @token_bp.input(token_create_input_schema, location="json", arg_name="token_data")
    @token_bp.output(token_output_schema)
    @token_bp.auth_required(auth, roles=[AuthRoles.RW])
    def create_token(token_data: TokenCreateInput) -> TokenOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        token = db.tokens.create_token(user.get_branch(), token_data.description)

        return TokenOutput(
            status="success",
            message="Token created successfully",
            data=token,
        )

    @token_bp.patch("/api/branch/@me/token/<string:token_id>")
    @token_bp.doc(summary="Update a Token", description="Update a Token by ID for a given branch", tags=["Tokens"])
    @token_bp.input(token_update_input_schema, location="json", arg_name="token_data")
    @token_bp.output(token_output_schema)
    @token_bp.auth_required(auth, roles=[AuthRoles.RW])
    def update_token(token_id: str, token_data: TokenUpdateInput) -> OutCanError[TokenOutput]:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        token, error = db.tokens.update_token(user.get_branch(), token_id, token_data.description)

        if error:
            return ErrorResponse(error)
        return TokenOutput(
            status="success",
            message="Token updated successfully",
            data=token,
        )

    @token_bp.post("/api/branch/@me/token/<string:token_id>/roll")
    @token_bp.doc(summary="Roll Token Value", description="Generate a new secret for a specific token", tags=["Tokens"])
    @token_bp.output(token_output_schema)
    @token_bp.auth_required(auth, roles=[AuthRoles.RW])
    def roll_token(token_id: str) -> OutCanError[TokenOutput]:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        token, error = db.tokens.roll_token(user.get_branch(), token_id)

        if error:
            return ErrorResponse(error)
        return TokenOutput(
            status="success",
            message="Token rolled successfully",
            data=token,
        )

    @token_bp.delete("/api/branch/@me/token/<string:token_id>")
    @token_bp.doc(summary="Delete a Token", description="Delete a Token by ID for a given branch", tags=["Tokens"])
    @token_bp.output(generic_output_schema)
    @token_bp.auth_required(auth, roles=[AuthRoles.RW])
    def delete_token(token_id: str) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.tokens.delete_token(user.get_branch(), token_id)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="Token deleted successfully",
        )

    app.register_blueprint(token_bp)
