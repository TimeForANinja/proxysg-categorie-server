from apiflask import APIBlueprint, APIFlask

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.history import ListHistoryOutput


def add_history_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding History Blueprint')
    auth_if = get_auth_if(app)
    history_bp = APIBlueprint('history', __name__)

    # Route to fetch all Categories
    @history_bp.get('/api/history')
    @history_bp.doc(summary='List Change History', description='List all Changes done to the Database')
    @history_bp.output(ListHistoryOutput)
    @history_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RO])
    def get_categories():
        db_if = get_db()
        histories = db_if.history.get_history_events()
        return {
            'status': 'success',
            'message': 'History fetched successfully',
            'data': [x.to_rest() for x in histories],
        }

    app.register_blueprint(history_bp)
