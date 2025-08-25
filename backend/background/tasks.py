from auth.auth_user import AuthUser
from db.db import DBInterface
from db.task import Task, CleanupFlags
from db.util.parse_existing_db import parse_db, create_in_db, create_urls_db
from log import log_debug, log_info


def execute_load_existing_task(db_if: DBInterface, task: Task):
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
        create_in_db(db_if, categories, prefix)
        create_urls_db(db_if, uncategorized)

        # Add history event
        db_if.history.add_history_event(
            'existing db imported via task',
            AuthUser(username=task.user, roles=[]),
            [],[],[]
        )

        log_info('BACKGROUND', f'Load existing task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing load_existing task {task.id}', {
            'error': str(e)
        })
        db_if.tasks.update_task_status(task.id, 'failed')


def execute_cleanup_existing(db_if: DBInterface, task: Task):
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
            urls = db_if.urls.get_all_urls()

            for url in urls:
                if len(url.categories) == 0:
                    log_debug("BACKGROUND", f"Deleting unused URL {url.id} for task {task.id}")
                    db_if.urls.delete_url(url.id)

            # Add history event
            db_if.history.add_history_event(
                'cleanup unused URLs via task',
                AuthUser(username=task.user, roles=[]),
                [], [], []
            )

        if flags & CleanupFlags.Categories:
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
                    db_if.categories.delete_category(cat.id)

            # Add history event
            db_if.history.add_history_event(
                'cleanup unused Categories via task',
                AuthUser(username=task.user, roles=[]),
                [], [], []
            )

        log_info('BACKGROUND', f'cleanup_existing task {task.id} completed successfully')
        db_if.tasks.update_task_status(task.id, 'success')
    except Exception as e:
        log_info('BACKGROUND', f'Error executing cleanup_existing task {task.id}', {
            'error': str(e)
        })
        db_if.tasks.update_task_status(task.id, 'failed')
