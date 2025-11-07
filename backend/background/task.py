import traceback

from db.dbmodel.task import CleanupFlags, Task
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


def execute_cleanup_existing(db_if: StagingDB, task: Task):
    """
    Execute a task to cleanup unused Elements (URLS / Categories).
    """
    log_debug('BACKGROUND', f'Executing cleanup_existing task {task.id}')

    # Update task status to running
    db_if.tasks.update_task_status(task.id, 'running')

    try:
        # validate and extract parameters
        # the parameters should be [func_name, flags]
        if len(task.parameters) != 2:
            # use the existing catch and error handling at the bottom
            raise Exception('Invalid parameters for cleanup_existing task')
        flags = CleanupFlags(task.parameters[1])

        if flags & CleanupFlags.URLs:
            log_debug("BACKGROUND", f"Cleanup URLs for task {task.id}")
            urls = db_if.urls.get_all_urls()

            for url in urls:
                if len(url.categories) == 0:
                    log_debug("BACKGROUND", f"Deleting unused URL {url.id} for task {task.id}")
                    db_if.urls.delete_url(task.user, url.id)

        if flags & CleanupFlags.Categories:
            log_debug("BACKGROUND", f"Cleanup Categories for task {task.id}")
            urls = db_if.urls.get_all_urls()
            cats = db_if.categories.get_all_categories()

            # Build a set of used category ids from URLs
            used_cat_ids = set()
            for url in urls:
                for cid in (url.categories or []):
                    used_cat_ids.add(cid)

            for cat in cats:
                is_used = cat.id in used_cat_ids
                if not cat.nested_categories and not is_used:
                    log_debug("BACKGROUND", f"Deleting unused Category {cat.id} for task {task.id}")
                    db_if.categories.delete_category(task.user, cat.id)

        log_info('BACKGROUND', f'cleanup_existing task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing cleanup_existing task {task.id}', {
            'error': str(e)
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
        # validate and extract parameters
        # the parameters should be [func_name, commit_message, time_of_creation]
        if len(task.parameters) != 3:
            # use the existing catch and error handling at the bottom
            raise Exception('Invalid parameters for commit task')
        commit_message = task.parameters[1]
        not_before = int(task.parameters[2])

        db_if.commit(task.user, commit_message, not_before)
        log_info('BACKGROUND', f'Commit task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing commit task {task.id}', {
            'error': str(e),
            'traceback': traceback.format_exc(),
        })
        db_if.tasks.update_task_status(task.id, 'failed')

def execute_revert(db_if: StagingDB, task: Task):
    """
    Execute a revert task.
    This will simply clear any staged changes

    :param db_if: The database interface to use
    :param task: the task to execute
    """
    log_debug('BACKGROUND', f'Executing revert task {task.id}')

    # Update task status to running
    db_if.tasks.update_task_status(task.id, 'running')

    try:
        db_if.revert()
        log_info('BACKGROUND', f'Revert task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing revert task {task.id}', {
            'error': str(e),
            'traceback': traceback.format_exc(),
        })
        db_if.tasks.update_task_status(task.id, 'failed')
