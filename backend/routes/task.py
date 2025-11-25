import time

from apiflask import APIBlueprint
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from db.dbmodel.task import MutableTask
from log import log_debug
from routes.schemas.commit import CommitInput
from routes.schemas.task import ExistingDBInput, ListTaskOutput, CreatedTaskOutput, SingleTaskOutput, CleanupInput


def add_task_bp(app):
    log_debug('ROUTES', 'Adding Task Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    task_bp = APIBlueprint('task', __name__)

    # Route to upload an existing category db
    @task_bp.post('/api/task/new/upload_existing_db')
    @task_bp.doc(summary='Upload existing DB', description='Upload an existing database to the server')
    @task_bp.input(class_schema(ExistingDBInput)(), location='json', arg_name='existing_db')
    @task_bp.output(CreatedTaskOutput)
    @task_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def load_existing(existing_db: ExistingDBInput):
        # Create a background task to process the database
        task = get_db().tasks.add_task(auth.current_user, MutableTask(
            name='load_existing',
            parameters=['load_existing', existing_db.categoryDB, existing_db.prefix]
        ))
        log_debug('API', f'Created load_existing task {task.id}')

        return {
            'status': 'success',
            'message': 'Database import task created successfully',
            'data': task.id,
        }

    # Route to create a task for cleanup of unused URLs / Categories
    @task_bp.post('/api/task/new/cleanup_unused')
    @task_bp.doc(summary='Cleanup Unused', description='Cleanup various unused objects')
    @task_bp.input(class_schema(CleanupInput)(), location='json', arg_name='cleanup_settings')
    @task_bp.output(CreatedTaskOutput)
    @task_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def cleanup_unused(cleanup_settings: CleanupInput):
        # Create a background task to process the cleanup
        task = get_db().tasks.add_task(auth.current_user, MutableTask(
            name='cleanup_unused',
            parameters=['cleanup_unused', cleanup_settings.flags]
        ))
        log_debug('API', f'Created cleanup_unused task {task.id}')

        return {
            'status': 'success',
            'message': 'Cleanup-Unused task created successfully',
            'data': task.id,
        }

    # Route to revert any not-commited changes
    @task_bp.post('/api/task/new/revert')
    @task_bp.doc(summary='Revert Changes', description='Revert any not-commited changes')
    @task_bp.output(CreatedTaskOutput)
    @task_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def revert_changes():
        # Create a background task to process the cleanup
        task = get_db().tasks.add_task(auth.current_user, MutableTask(
            name='revert_uncommitted',
            parameters=['revert_uncommitted']
        ))
        log_debug('API', f'Created revert_uncommitted task {task.id}')

        return {
            'status': 'success',
            'message': 'Revert task created successfully',
            'data': task.id,
        }

    # Route to get all tasks
    @task_bp.get('/api/task')
    @task_bp.doc(summary='Get all tasks', description='Get a list of all tasks and their status')
    @task_bp.output(ListTaskOutput)
    @task_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_tasks():
        tasks = get_db().tasks.get_all_tasks()
        return {
            'status': 'success',
            'message': 'Tasks fetched successfully',
            'data': [x.to_rest() for x in tasks],
        }

    # Route to get a single task by ID
    @task_bp.get('/api/task/<string:task_id>')
    @task_bp.doc(summary='Get a single task', description='Get details of a specific task by its ID')
    @task_bp.output(SingleTaskOutput)
    @task_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_task(task_id):
        task = get_db().tasks.get_task(task_id)

        if task is None:
            return {
                'status': 'failed',
                'message': 'Task not found',
            }, 404

        return {
            'status': 'success',
            'message': 'Task fetched successfully',
            'data': task.to_rest(),
        }

    @task_bp.post('/api/task/new/commit')
    @task_bp.doc(summary='Commit Staged Changes', description='Create a Task to commit all staged changes to the database')
    @task_bp.input(class_schema(CommitInput)(), location='json', arg_name='commit_data')
    @task_bp.output(CreatedTaskOutput)
    @task_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def handle_commit(commit_data: CommitInput):
        # Create a background task to process the database
        task = get_db().tasks.add_task(auth.current_user, MutableTask(
            name='commit',
            parameters=['commit', commit_data.message, str(int(time.time()))]
        ))
        log_debug('API', f'Created commit task {task.id} with message: {commit_data.message}')

        return {
            'status': 'success',
            'message': 'Commit task created successfully',
            'data': task.id,
        }

    @task_bp.post('/api/task/new/refresh_bc')
    @task_bp.doc(summary='Refresh BC Categories', description='Trigger a refresh of all BC Categories')
    @task_bp.output(CreatedTaskOutput)
    @task_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def handle_refresh_bc():
        # Create a background task to process the refresh
        task = get_db().tasks.add_task(auth.current_user, MutableTask(
            name='refresh_bc',
            parameters=['refresh_bc']
        ))
        log_debug('API', f'Created refresh_bc task {task.id}')

        return {
            'status': 'success',
            'message': 'Commit task created successfully',
            'data': task.id,
        }

    app.register_blueprint(task_bp)
