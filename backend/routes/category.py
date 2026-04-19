from typing import cast
from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from util.log import log_debug
from routes.schemas.category import ListCategoryOutput, CategoryOutput, \
    url_category_mapping_input_schema, URLCategoryMappingInput, ConstrainedURLListOutput, category_output_schema, \
    list_category_output_schema, constrained_url_list_output_schema, ChildCategoryMappingInput, ChildCategoryListOutput, \
    child_category_mapping_input_schema, child_category_list_output_schema, \
    CategoryInput, category_input_schema
from routes.schemas.error import ErrorResponse, OutCanError
from routes.schemas.generic_output import GenericOutput, generic_output_schema


def add_category_bp(app: APIFlask):
    log_debug("ROUTES", "Adding Category Blueprint")
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    category_bp = APIBlueprint("Categories", __name__)


    @category_bp.get("/api/branch/<branch>/category")
    @category_bp.doc(summary="List all Categories", description="List all Categories for a given branch", tags=["Categories"])
    @category_bp.output(list_category_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_categories(branch: str) -> ListCategoryOutput:
        db = get_db()
        categories = db.specials.fetch_categories(branch)
        return ListCategoryOutput(
            status="success",
            message="Categories fetched successfully",
            data=categories,
        )

    @category_bp.post("/api/branch/@me/category")
    @category_bp.doc(summary="Create a Category", description="Create a new Category for a given branch", tags=["Categories"])
    @category_bp.input(category_input_schema, location="json", arg_name="category_data")
    @category_bp.output(category_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
    def create_category(category_data: CategoryInput) -> CategoryOutput:
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

    @category_bp.put("/api/branch/@me/category/<category_id>")
    @category_bp.doc(summary="Update a Category", description="Update a Category by ID for a given branch", tags=["Categories"])
    @category_bp.input(category_input_schema, location="json", arg_name="category_data")
    @category_bp.output(category_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
    def update_category(category_id: str, category_data: CategoryInput) -> OutCanError[CategoryOutput]:
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


    @category_bp.get("/api/branch/<branch>/category/<category_id>/url")
    @category_bp.doc(summary="List all URLs in Category", description="List all URLs and their constraints for a given category", tags=["Categories", "URLs", "Mapping"])
    @category_bp.output(constrained_url_list_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_category_urls(branch: str, category_id: str) -> ConstrainedURLListOutput:
        db = get_db()
        constrained_urls = db.mappings.get_category_urls(branch, category_id)
        return ConstrainedURLListOutput(
            status="success",
            message="Category URL mappings fetched successfully",
            data=constrained_urls,
        )

    @category_bp.post("/api/branch/@me/category/<category_id>/url")
    @category_bp.doc(summary="Add URL to Category", description="Add a new URL mapping to a category", tags=["Categories", "URLs", "Mapping"])
    @category_bp.input(url_category_mapping_input_schema, location="json", arg_name="mapping_data")
    @category_bp.output(generic_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
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

    @category_bp.delete("/api/branch/@me/category/<category_id>/url/<url_id>")
    @category_bp.doc(summary="Remove URL from Category", description="Remove a URL mapping from a category", tags=["Categories", "URLs", "Mapping"])
    @category_bp.output(generic_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
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


    @category_bp.get("/api/branch/<branch>/category/<category_id>/parent")
    @category_bp.doc(summary="Get Super Categories", description="Get the child categories for a given category", tags=["Categories", "Mapping"])
    @category_bp.output(child_category_list_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_child_category(branch: str, category_id: str) -> ChildCategoryListOutput:
        db = get_db()
        child_categories = db.mappings.get_child_categories(branch, category_id)
        return ChildCategoryListOutput(
            status="success",
            message="Super-Categories fetched successfully",
            data=child_categories,
        )

    @category_bp.post("/api/branch/@me/category/<category_id>/parent")
    @category_bp.doc(summary="Add Super Category", description="Add a child category to a category", tags=["Categories", "Mapping"])
    @category_bp.input(child_category_mapping_input_schema, location="json", arg_name="mapping_data")
    @category_bp.output(generic_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
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

    @category_bp.delete("/api/branch/@me/category/<category_id>/parent/<child_category_id>")
    @category_bp.doc(summary="Remove Super Category", description="Remove a parent category from a category", tags=["Categories", "Mapping"])
    @category_bp.output(generic_output_schema)
    @category_bp.auth_required(auth, roles=[AuthRoles.RW])
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

    app.register_blueprint(category_bp)
