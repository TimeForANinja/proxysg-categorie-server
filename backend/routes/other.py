from apiflask import APIBlueprint
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from db.task import MutableTask
from log import log_debug
from routes.schemas.load_existing import ExistingDBInput
from routes.schemas.tasks import ListTaskOutput, CreatedTaskOutput


def add_other_bp(app):
    log_debug('ROUTES', 'Adding other Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    other_bp = APIBlueprint('other', __name__)

    # Route to upload an existing category db
    @other_bp.post('/api/upload_existing_db')
    @other_bp.doc(summary='Upload existing DB', description='Upload an existing database to the server')
    @other_bp.input(class_schema(ExistingDBInput)(), location='json', arg_name='existing_db')
    @other_bp.output(CreatedTaskOutput)
    @other_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def load_existing(existing_db: ExistingDBInput):
        db_if = get_db()

        # Create a background task to process the database
        task = db_if.tasks.add_task(auth.current_user, MutableTask(
            name='load_existing',
            parameters=['load_existing', existing_db.categoryDB, existing_db.prefix]
        ))
        log_debug('API', f'Created load_existing task {task.id}')

        return {
            'status': 'success',
            'message': 'Database import task created successfully',
            'data': task.id,
        }

    # Route to get all tasks
    @other_bp.get('/api/tasks')
    @other_bp.doc(summary='Get all tasks', description='Get a list of all tasks and their status')
    @other_bp.output(ListTaskOutput)
    @other_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_tasks():
        db_if = get_db()
        tasks = db_if.tasks.get_all_tasks()
        return {
            'status': 'success',
            'message': 'Tasks fetched successfully',
            'data': tasks,
        }

    app.register_blueprint(other_bp)
