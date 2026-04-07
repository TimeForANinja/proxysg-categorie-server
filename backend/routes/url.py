from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.url import ListURLOutput
from routes.schemas.branch import BranchQuery

def add_url_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding URL Blueprint')
    url_bp = APIBlueprint('url', __name__)

    @url_bp.get('/api/url')
    @url_bp.doc(summary='List all URLs', description='List all URLs and their categories for a given branch')
    @url_bp.input(BranchQuery, location='query')
    @url_bp.output(ListURLOutput)
    def get_urls(query_data):
        branch = query_data.get('branch')
        db = get_db()
        urls = db.specials.fetch_url_list(branch)
        return {
            'status': 'success',
            'message': 'URLs fetched successfully',
            'data': urls,
        }

    app.register_blueprint(url_bp)
