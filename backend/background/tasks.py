from auth.auth_user import AuthUser
from db.abc.task import Task
from db.stagingdb.db import StagingDB
from db.util.parse_existing_db import parse_db, create_in_db, create_urls_db
from log import log_debug, log_info

def execute_load_existing_task(db_if: StagingDB, task: Task):
    """
    Execute a load_existing task.

    :param db_if: The database interface to use
    :param task: the task to execute
    """
    log_debug('BACKGROUND', f'Executing load_existing task {task.id}')

    # Update task status to running
    db_if.tasks.update_task_status(task.id, 'running')

    try:
        # validate and extract parameters
        # the parameters should be [func_name, categoryDB, prefix]
        if len(task.parameters) != 3:
            # use the existing catch and error handling at the bottom
            raise Exception('Invalid parameters for load_existing task')
        category_db = task.parameters[1]
        prefix = task.parameters[2]

        # Parse DB into intermediate objects
        categories, uncategorized = parse_db(category_db, True)

        # Push the intermediate objects to the main DB
        create_in_db(db_if.urls, db_if.categories, db_if.url_categories, AuthUser.unserialize(task.user), categories, prefix)
        create_urls_db(db_if.urls, AuthUser.unserialize(task.user), uncategorized)

        log_info('BACKGROUND', f'Load existing task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing load_existing task {task.id}', {
            'error': str(e)
        })
        db_if.tasks.update_task_status(task.id, 'failed')
