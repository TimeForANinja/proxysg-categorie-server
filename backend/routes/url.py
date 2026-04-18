from typing import cast
from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from util.log import log_debug
from routes.schemas.error import OutCanError, ErrorResponse
from routes.schemas.generic_output import generic_output_schema, GenericOutput
from routes.schemas.url import ListURLOutput, list_url_output_schema, url_input_schema, url_output_schema, URLInput, \
    URLOutput


def add_url_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding URL Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    url_bp = APIBlueprint('URLs', __name__, tag='URLs')


    @url_bp.get('/api/branch/<branch>/url')
    @url_bp.doc(summary='List all URLs', description='List all URLs and their categories for a given branch', tags=['URLs'])
    @url_bp.output(list_url_output_schema)
    @url_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_urls(branch: str) -> ListURLOutput:
        db = get_db()
        urls = db.specials.fetch_url_list(branch)
        return ListURLOutput(
            status='success',
            message='URLs fetched successfully',
            data=urls,
        )

    @url_bp.post('/api/branch/@me/url')
    @url_bp.doc(summary='Create a URL', description='Create a new URL for a user branch', tags=['URLs'])
    @url_bp.input(url_input_schema, location='json', arg_name='url_data')
    @url_bp.output(url_output_schema)
    @url_bp.auth_required(auth, roles=[AuthRoles.RW])
    def create_url(url_data: URLInput) -> URLOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        url = db.urls.create_url(user.get_branch(), url_data.url)

        return URLOutput(
            status='success',
            message='URL created successfully',
            data=url,
        )

    @url_bp.put('/api/branch/@me/url/<url_id>')
    @url_bp.doc(summary='Update a URL', description='Update a URL by ID for a given branch', tags=['URLs'])
    @url_bp.input(url_input_schema, location='json', arg_name='url_data')
    @url_bp.output(url_output_schema)
    @url_bp.auth_required(auth, roles=[AuthRoles.RW])
    def update_url(url_id: str, url_data: URLInput) -> OutCanError[URLOutput]:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        url, error = db.urls.update_url(user.get_branch(), url_id, url_data.url)

        if error:
            return ErrorResponse(error)
        return URLOutput(
            status='success',
            message='URL updated successfully',
            data=url,
        )

    @url_bp.delete('/api/branch/@me/url/<url_id>')
    @url_bp.doc(summary='Delete a URL', description='Delete a URL by ID for a given branch', tags=['URLs'])
    @url_bp.output(generic_output_schema)
    @url_bp.auth_required(auth, roles=[AuthRoles.RW])
    def delete_url(url_id: str) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        error = db.urls.delete_url(user.get_branch(), url_id)

        if error:
            return ErrorResponse(error)
        return GenericOutput(
            status='success',
            message='URL deleted successfully',
        )

    app.register_blueprint(url_bp)
