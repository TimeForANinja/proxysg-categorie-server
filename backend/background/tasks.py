import traceback

from db.dbmodel.task import Task
from db.middleware.stagingdb.db import StagingDB
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
        create_in_db(db_if, task.user, categories, prefix)
        create_urls_db(db_if, task.user, uncategorized)

        log_info('BACKGROUND', f'Load existing task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing load_existing task {task.id}', {
            'error': str(e),
            'traceback': traceback.format_exc(),
        })
        db_if.tasks.update_task_status(task.id, 'failed')

def execute_commit(db_if: StagingDB, task: Task):
    """
    Execute a commit task.

    :param db_if: The database interface to use
    :param task: the task to execute
    """
    log_debug('BACKGROUND', f'Executing commit task {task.id}')

    # Update task status to running
    db_if.tasks.update_task_status(task.id, 'running')

    try:
        db_if.commit(task.user)
        log_info('BACKGROUND', f'Commit task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing commit task {task.id}', {
            'error': str(e),
            'traceback': traceback.format_exc(),
        })
        db_if.tasks.update_task_status(task.id, 'failed')
