from typing import cast
from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from routes.schemas.mappings import token_category_mapping_input_schema, TokenCategoryMappingInput
from util.log import log_debug
from routes.schemas.mappings import url_category_mapping_input_schema, URLCategoryMappingInput, \
    ConstrainedURLListOutput, constrained_url_list_output_schema, ChildCategoryMappingInput, ChildCategoryListOutput, \
    child_category_mapping_input_schema, child_category_list_output_schema, list_category_output_schema, \
    ListCategoryOutput
from routes.schemas.error import ErrorResponse
from routes.schemas.generic_output import GenericOutput, generic_output_schema


def add_mapping_bp(app: APIFlask):
    log_debug("ROUTES", "Adding Mapping Blueprint")
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    mapping_bp = APIBlueprint("Mapping", __name__)


    @mapping_bp.get("/api/branch/<branch>/category/<category_id>/url")
    @mapping_bp.doc(summary="List all URLs in Category", description="List all URLs and their constraints for a given category", tags=["Categories", "URLs", "Mapping"])
    @mapping_bp.output(constrained_url_list_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_category_urls(branch: str, category_id: str) -> ConstrainedURLListOutput:
        db = get_db()
        constrained_urls = db.mappings.get_category_urls(branch, category_id)
        return ConstrainedURLListOutput(
            status="success",
            message="Category URL mappings fetched successfully",
            data=constrained_urls,
        )

    @mapping_bp.post("/api/branch/@me/category/<category_id>/url")
    @mapping_bp.doc(summary="Add URL to Category", description="Add a new URL mapping to a category", tags=["Categories", "URLs", "Mapping"])
    @mapping_bp.input(url_category_mapping_input_schema, location="json", arg_name="mapping_data")
    @mapping_bp.output(generic_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RW])
    def add_category_url(category_id: str, mapping_data: URLCategoryMappingInput) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.mappings.add_url_category(
            user.get_branch(),
            category_id,
            mapping_data.url_id,
            mapping_data.constraint,
        )

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="URL added to category successfully",
        )

    @mapping_bp.delete("/api/branch/@me/category/<category_id>/url/<url_id>")
    @mapping_bp.doc(summary="Remove URL from Category", description="Remove a URL mapping from a category", tags=["Categories", "URLs", "Mapping"])
    @mapping_bp.output(generic_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RW])
    def delete_category_url(category_id: str, url_id: str) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.mappings.delete_url_category(user.get_branch(), category_id, url_id)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="URL removed from category successfully",
        )


    @mapping_bp.get("/api/branch/<branch>/category/<category_id>/child")
    @mapping_bp.doc(summary="Get Super Categories", description="Get the child categories for a given category", tags=["Categories", "Mapping"])
    @mapping_bp.output(child_category_list_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_child_category(branch: str, category_id: str) -> ChildCategoryListOutput:
        db = get_db()
        child_categories = db.mappings.get_child_categories(branch, category_id)
        return ChildCategoryListOutput(
            status="success",
            message="Super-Categories fetched successfully",
            data=child_categories,
        )

    @mapping_bp.post("/api/branch/@me/category/<category_id>/child")
    @mapping_bp.doc(summary="Add Super Category", description="Add a child category to a category", tags=["Categories", "Mapping"])
    @mapping_bp.input(child_category_mapping_input_schema, location="json", arg_name="mapping_data")
    @mapping_bp.output(generic_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RW])
    def add_child_category(category_id: str, mapping_data: ChildCategoryMappingInput) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.mappings.add_child_category(
            user.get_branch(),
            category_id,
            mapping_data.child_category_id,
        )

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="Super-Category added successfully",
        )

    @mapping_bp.delete("/api/branch/@me/category/<category_id>/child/<child_category_id>")
    @mapping_bp.doc(summary="Remove Super Category", description="Remove a child category from a category", tags=["Categories", "Mapping"])
    @mapping_bp.output(generic_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RW])
    def delete_child_category(category_id: str, child_category_id: str) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.mappings.delete_child_category(user.get_branch(), category_id, child_category_id)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="URL removed from category successfully",
        )


    @mapping_bp.get("/api/branch/<branch>/token/<token_id>/category")
    @mapping_bp.doc(summary="List all Category of Token", description="List all categories of a specific token for a given branch", tags=["Tokens", "Categories", "Mapping"])
    @mapping_bp.output(list_category_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_token_categories(branch: str, token_id: str) -> ListCategoryOutput:
        db = get_db()
        categories = db.mappings.get_token_categories(branch, token_id)
        return ListCategoryOutput(
            status="success",
            message="Token category mappings fetched successfully",
            data=categories,
        )

    @mapping_bp.post("/api/branch/@me/token/<token_id>/category")
    @mapping_bp.doc(summary="Associate Token with Category", description="Add a category to a token", tags=["Tokens", "Categories", "Mapping"])
    @mapping_bp.input(token_category_mapping_input_schema, location="json", arg_name="mapping_data")
    @mapping_bp.output(generic_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RW])
    def add_token_category(token_id: str, mapping_data: TokenCategoryMappingInput) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.mappings.add_token_category(user.get_branch(), token_id, mapping_data.category_id)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="Category added to token successfully",
        )

    @mapping_bp.delete("/api/branch/@me/token/<token_id>/category/<category_id>")
    @mapping_bp.doc(summary="Disassociate Token from Category", description="Remove a category from a token", tags=["Tokens", "Categories", "Mapping"])
    @mapping_bp.output(generic_output_schema)
    @mapping_bp.auth_required(auth, roles=[AuthRoles.RW])
    def delete_token_category(token_id: str, category_id: str) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.mappings.delete_token_category(user.get_branch(), token_id, category_id)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="Category removed from token successfully",
        )

    app.register_blueprint(mapping_bp)
