from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.category import ListCategoryOutput, CategoryOutput, category_input_schema, CategoryInput, \
    url_category_mapping_input_schema, URLCategoryMappingInput, ConstrainedURLListOutput, category_output_schema, \
    list_category_output_schema, constrained_url_list_output_schema
from routes.schemas.error import ErrorResponse
from routes.schemas.generic_output import GenericOutput, generic_output_schema


def add_category_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Category Blueprint')
    category_bp = APIBlueprint('Categories', __name__)


    @category_bp.get('/api/branch/<branch>/category')
    @category_bp.doc(summary='List all Categories', description='List all Categories for a given branch', tags=['Categories'])
    @category_bp.output(list_category_output_schema)
    def get_categories(branch: str) -> ListCategoryOutput:
        db = get_db()
        categories = db.specials.fetch_categories(branch)
        return ListCategoryOutput(
            status='success',
            message='Categories fetched successfully',
            data=categories,
        )

    @category_bp.post('/api/branch/<branch>/category')
    @category_bp.doc(summary='Create a Category', description='Create a new Category for a given branch', tags=['Categories'])
    @category_bp.input(category_input_schema, location='json', arg_name='category_data')
    @category_bp.output(category_output_schema)
    def create_category(branch: str, category_data: CategoryInput) -> CategoryOutput:
        db = get_db()
        category = db.categories.create_category(branch, category_data.name)
        return CategoryOutput(
            status='success',
            message='Category created successfully',
            data=category,
        )

    @category_bp.delete('/api/branch/<branch>/category/<category_id>')
    @category_bp.doc(summary='Delete a Category', description='Delete a Category by ID for a given branch', tags=['Categories'])
    @category_bp.output(generic_output_schema)
    def delete_category(branch: str, category_id: str) -> GenericOutput:
        db = get_db()
        error = db.categories.delete_category(branch, category_id)
        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='Category deleted successfully',
        )


    @category_bp.get('/api/branch/<branch>/category/<category_id>/url')
    @category_bp.doc(summary='List all URLs in Category', description='List all URLs and their constraints for a given category', tags=['Categories', 'Urls', 'Mapping'])
    @category_bp.output(constrained_url_list_output_schema)
    def get_category_urls(branch: str, category_id: str) -> ConstrainedURLListOutput:
        db = get_db()
        constrained_urls = db.mappings.get_category_urls(branch, category_id)
        return ConstrainedURLListOutput(
            status='success',
            message='Category URL mappings fetched successfully',
            data=constrained_urls,
        )

    @category_bp.post('/api/branch/<branch>/category/<category_id>/url')
    @category_bp.doc(summary='Add URL to Category', description='Add a new URL mapping to a category', tags=['Categories', 'Urls', 'Mapping'])
    @category_bp.input(url_category_mapping_input_schema, location='json', arg_name='mapping_data')
    @category_bp.output(generic_output_schema)
    def add_category_url(branch: str, category_id: str, mapping_data: URLCategoryMappingInput) -> GenericOutput:
        db = get_db()
        error = db.mappings.add_url_category(
            branch,
            category_id,
            mapping_data.url,
            mapping_data.constraint,
        )
        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='URL added to category successfully',
        )

    @category_bp.delete('/api/branch/<branch>/category/<category_id>/url/<url>')
    @category_bp.doc(summary='Remove URL from Category', description='Remove a URL mapping from a category', tags=['Categories', 'Urls', 'Mapping'])
    @category_bp.output(generic_output_schema)
    def delete_category_url(branch: str, category_id: str, url: str) -> GenericOutput:
        db = get_db()
        error = db.mappings.delete_url_category(branch, category_id, url)
        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='URL removed from category successfully',
        )

    app.register_blueprint(category_bp)
