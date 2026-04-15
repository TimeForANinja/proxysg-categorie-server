from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.error import OutCanError, ErrorResponse
from routes.schemas.generic_output import generic_output_schema, GenericOutput
from routes.schemas.url import ListURLOutput, list_url_output_schema, url_input_schema, url_output_schema, URLInput, \
    URLOutput


def add_url_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding URL Blueprint')
    url_bp = APIBlueprint('Urls', __name__)

    @url_bp.get('/api/branch/<branch>/url')
    @url_bp.doc(summary='List all URLs', description='List all URLs and their categories for a given branch', tags=['Urls'])
    @url_bp.output(list_url_output_schema)
    def get_urls(branch: str) -> ListURLOutput:
        db = get_db()
        urls = db.specials.fetch_url_list(branch)
        return ListURLOutput(
            status='success',
            message='URLs fetched successfully',
            data=urls,
        )

    @url_bp.post('/api/branch/<branch>/url')
    @url_bp.doc(summary='Create a URL', description='Create a new URL for a given branch', tags=['Urls'])
    @url_bp.input(url_input_schema, location='json', arg_name='url_data')
    @url_bp.output(url_output_schema)
    def create_url(branch: str, url_data: URLInput) -> URLOutput:
        db = get_db()
        url = db.urls.create_url(branch, url_data.url)
        return URLOutput(
            status='success',
            message='URL created successfully',
            data=url,
        )

    @url_bp.put('/api/branch/<branch>/url/<url_id>')
    @url_bp.doc(summary='Update a URL', description='Update a URL by ID for a given branch', tags=['Urls'])
    @url_bp.input(url_input_schema, location='json', arg_name='url_data')
    @url_bp.output(url_output_schema)
    def update_url(branch: str, url_id: str, url_data: URLInput) -> OutCanError[URLOutput]:
        db = get_db()
        url, error = db.urls.update_url(branch, url_id, url_data.url)
        if error:
            return ErrorResponse(error)
        return URLOutput(
            status='success',
            message='URL updated successfully',
            data=url,
        )

    @url_bp.delete('/api/branch/<branch>/url/<url_id>')
    @url_bp.doc(summary='Delete a URL', description='Delete a URL by ID for a given branch', tags=['Urls'])
    @url_bp.output(generic_output_schema)
    def delete_url(branch: str, url_id: str) -> GenericOutput:
        db = get_db()
        error = db.urls.delete_url(branch, url_id)
        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='URL deleted successfully',
        )

    app.register_blueprint(url_bp)
