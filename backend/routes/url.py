from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.url import ListURLOutput, list_url_output_schema


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

    app.register_blueprint(url_bp)
