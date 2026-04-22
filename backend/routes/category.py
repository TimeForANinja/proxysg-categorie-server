from typing import cast
from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from util.log import log_debug
from routes.schemas.category import category_output_schema, category_create_input_schema, category_update_input_schema, \
    CategoryCreateInput, CategoryUpdateInput, CategoryOutput, ListCategoryDetailsOutput, \
    list_category_detail_output_schema, list_category_query_schema, ListCategoriesQuery
from routes.schemas.error import ErrorResponse, OutCanError
from routes.schemas.generic_output import GenericOutput, generic_output_schema


def add_category_bp(app: APIFlask):
    log_debug("ROUTES", "Adding Category Blueprint")
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    category_bp = APIBlueprint("Categories", __name__)


    @category_bp.get("/api/branch/<branch>/category")
    @category_bp.doc(summary="List all Categories", description="List all Categories for a given branch", tags=["Categories"])
    @category_bp.input(list_category_query_schema, location="query", arg_name="flags")
    @category_bp.output(list_category_detail_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_categories(branch: str, flags: ListCategoriesQuery) -> ListCategoryDetailsOutput:
        db = get_db()
        categories = db.categories.fetch_categories(branch, flags.add_mappings)
        return ListCategoryDetailsOutput(
            status="success",
            message="Categories fetched successfully",
            data=categories,
        )

    @category_bp.post("/api/branch/@me/category")
    @category_bp.doc(summary="Create a Category", description="Create a new Category for a given branch", tags=["Categories"])
    @category_bp.input(category_create_input_schema, location="json", arg_name="category_data")
    @category_bp.output(category_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
    def create_category(category_data: CategoryCreateInput) -> CategoryOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        category = db.categories.create_category(
            user.get_branch(),
            category_data.name,
            category_data.description,
            category_data.color,
        )

        return CategoryOutput(
            status="success",
            message="Category created successfully",
            data=category,
        )

    @category_bp.patch("/api/branch/@me/category/<category_id>")
    @category_bp.doc(summary="Update a Category", description="Update a Category by ID for a given branch", tags=["Categories"])
    @category_bp.input(category_update_input_schema, location="json", arg_name="category_data")
    @category_bp.output(category_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
    def update_category(category_id: str, category_data: CategoryUpdateInput) -> OutCanError[CategoryOutput]:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        category, error = db.categories.update_category(
            user.get_branch(),
            category_id,
            category_data.name,
            category_data.description,
            category_data.color,
        )

        if error:
            return ErrorResponse(error)
        return CategoryOutput(
            status="success",
            message="Category updated successfully",
            data=category,
        )

    @category_bp.delete("/api/branch/@me/category/<category_id>")
    @category_bp.doc(summary="Delete a Category", description="Delete a Category by ID for a given branch", tags=["Categories"])
    @category_bp.output(generic_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
    def delete_category(category_id: str) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.categories.delete_category(user.get_branch(), category_id)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status="success",
            message="Category deleted successfully",
        )

    app.register_blueprint(category_bp)
