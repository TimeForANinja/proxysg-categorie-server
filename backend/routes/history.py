from apiflask import APIBlueprint, APIFlask
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.history import ListHistoryOutput, ListAtomicsOutput, GetHistoryQuery


def add_history_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding History Blueprint')
    auth_if = get_auth_if(app)
    history_bp = APIBlueprint('history', __name__)

    # Route to fetch History (optionally include atomics)
    @history_bp.get('/api/history')
    @history_bp.doc(
        summary='List Change History',
        description='List all Changes done to the Database. Use query param include_atomics=true to include atomics in the response.'
    )
    @history_bp.input(class_schema(GetHistoryQuery), location='query', arg_name='hist_query')
    @history_bp.output(ListHistoryOutput)
    @history_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RO])
    def get_history(hist_query: GetHistoryQuery):
        histories = get_db().history.get_history_events(include_atomics=hist_query.include_atomics)
        return {
            'status': 'success',
            'message': 'History fetched successfully',
            'data': [x.to_rest() for x in histories],
        }

    # Route to fetch Atomics for a specific History item
    @history_bp.get('/api/history/<string:history_id>/atomics')
    @history_bp.doc(
        summary='List History Atomics',
        description='List atomic changes for a specific history event. Use history_id "-1" to fetch pending staged atomics.'
    )
    @history_bp.output(ListAtomicsOutput)
    @history_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RO])
    def get_history_atomics(history_id: str):
        atomics = get_db().history.get_history_atomics(references_history=[history_id])
        return {
            'status': 'success',
            'message': 'Atomics fetched successfully',
            'data': [x.to_rest() for x in atomics],
        }

    app.register_blueprint(history_bp)
