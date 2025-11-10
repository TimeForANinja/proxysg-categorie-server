import traceback
import urllib3
from datetime import timedelta, datetime, timezone
from apiflask import APIFlask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from background.query_bc import ServerCredentials, query_all
from background.load_existing_db import load_existing_file
from background.task import execute_load_existing_task, execute_commit, execute_cleanup_existing, execute_revert
from db.db_singleton import get_db
from db.middleware.stagingdb.db import StagingDB
from log import log_debug, log_error

TIME_MINUTES = 60

# Allows up to 15 minutes as a grace period if the Scheduler is busy / blocked by other stuff
MISFIRE_GRACE_TIME = 15 * TIME_MINUTES


def start_background_tasks(app: APIFlask):
    """Initialize all background tasks"""

    # load required config variables
    tz = app.config.get('TIMEZONE', 'Europe/Berlin')

    log_debug('BACKGROUND', 'Starting Background Tasks...', { 'tz': tz })

    # Prepare the Scheduler
    scheduler = BackgroundScheduler({'apscheduler.timezone': tz})

    # add all tasks
    start_query_bc(scheduler, app, tz)
    start_load_existing(scheduler, app)
    start_task_scheduler(scheduler, app)

    # Start the Scheduler
    scheduler.start()


def start_load_existing(scheduler: BackgroundScheduler, app: APIFlask):
    """
    Initialize the background task to load an existing LocalDB File.
    Currently only done once after startup.

    :param scheduler: The scheduler to use
    :param app: The flask app to use
    """

    # load required config variables
    load_existing_path = app.config.get('LOAD_EXISTING', {}).get('PATH', './data/local_db.txt')
    load_existing_prefix = app.config.get('LOAD_EXISTING', {}).get('PREFIX', '')

    log_debug('BACKGROUND', 'Preparing Background Tasks "start_load_existing"', {
        'path': load_existing_path,
        'prefix': load_existing_prefix,
    })

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as a flask global object
    def query_executor(a: APIFlask):
        with a.app_context():
            try:
                log_debug('BACKGROUND', 'executing load_existing background task')
                load_existing_file(
                    filepath=load_existing_path,
                    prefix_cats=load_existing_prefix,
                )
            except Exception as e:
                log_error('BACKGROUND', 'Error executing load_existing background task', {
                    'error': str(e),
                    'traceback': traceback.format_exc(),
                })

    # run once 'quick' after 1 minute
    scheduler.add_job(
        lambda: query_executor(app),
        'date',
        run_date=datetime.now(timezone.utc) + timedelta(seconds=1*TIME_MINUTES),
        misfire_grace_time=MISFIRE_GRACE_TIME,
        id='task_load_existing',
    )


def start_task_scheduler(scheduler: BackgroundScheduler, app: APIFlask):
    """
    Initialize the background task to check for pending tasks and start them.

    :param scheduler: The scheduler to use
    :param app: The flask app to use
    """
    log_debug('BACKGROUND', 'Preparing Background Tasks "start_task_scheduler"')

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as a flask global object
    def task_executor(a: APIFlask):
        with a.app_context():
            try:
                log_debug('BACKGROUND', 'executing task_scheduler background task')
                db_if = get_db()

                # try to fetch the next pending task from the DB
                task = db_if.tasks.get_next_pending_task()
                log_debug("BACKGROUND", "next pending task", task, exclude_keys=("parameters",))

                # if a task is defined go based on the task.name
                # if no task is defined, we do nothing
                if task and task.name == "load_existing":
                    execute_load_existing_task(db_if, task)
                elif task and task.name == 'cleanup_unused':
                    execute_cleanup_existing(db_if, task)
                elif task and task.name == "commit":
                    if isinstance(db_if, StagingDB):
                        execute_commit(db_if, task)
                    else:
                        log_error('BACKGROUND', 'Cannot commit to non-staging DB')
                        db_if.tasks.update_task_status(task.id, 'failed')
                elif task and task.name == 'revert_uncommitted':
                    if isinstance(db_if, StagingDB):
                        execute_revert(db_if, task)
                    else:
                        log_error('BACKGROUND', 'Cannot revert uncommitted changes to non-staging DB')
                        db_if.tasks.update_task_status(task.id, 'failed')
                elif task:
                    log_debug('BACKGROUND', f'Unknown task type: {task.name} in task {task.id}')
                    db_if.tasks.update_task_status(task.id, 'unknown')
            except Exception as e:
                log_error('BACKGROUND', 'Error executing task_scheduler background task', {
                    'error': str(e),
                    'traceback': traceback.format_exc(),
                })

    # run every 30 seconds
    scheduler.add_job(
        lambda: task_executor(app),
        'interval',
        seconds=30,
        misfire_grace_time=MISFIRE_GRACE_TIME,
        id='check_task_queue',
    )


def start_query_bc(scheduler: BackgroundScheduler, app: APIFlask, tz: str):
    """
    Initialize the background task to query URL Categories from Bluecoat DB
    This is only possible with the Mgmt API of a Proxy Device

    :param scheduler: The scheduler to use
    :param app: The flask app to use
    :param tz: The timezone to use for cron triggers
    """

    # load required config variables
    query_bc_conf: dict = app.config.get('BC', {})
    bc_interval = query_bc_conf.get('INTERVAL', '0 3 * * *')
    bc_ttl = int(query_bc_conf.get('TTL', 7 * 24 * 60)) * TIME_MINUTES
    bc_host = query_bc_conf.get('HOST')
    bc_user = query_bc_conf.get('USER', 'ro_admin')
    bc_password = query_bc_conf.get('PASSWORD')
    # check for false or not false, so that we default to 'true' for all other values
    bc_verify_ssl = query_bc_conf.get('VERIFY_SSL', 'true').lower() != 'false'

    log_debug('BACKGROUND', 'Preparing Background Tasks "start_query_bc"', {
        'interval': bc_interval,
        'ttl': bc_ttl,
        'host': bc_host,
        'user': bc_user,
        'verify_ssl': bc_verify_ssl,
    })

    if not bc_verify_ssl:
        # hide warnings telling us to enable ssl verification
        urllib3.disable_warnings()

    # build a credential object to make it easier to pass them around
    credentials = ServerCredentials(
        server=bc_host,
        user=bc_user,
        password=bc_password,
        verifySSL=bc_verify_ssl,
    )

    def startup_and_enable_schedule():
        query_executor(app, credentials, bc_ttl)
        # add the long-terms chedule
        scheduler.add_job(
            lambda: query_executor(app, credentials, bc_ttl),
            CronTrigger.from_crontab(bc_interval, timezone=tz),
            misfire_grace_time=MISFIRE_GRACE_TIME,
            id='query_bc_cron',
        )

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as a flask global object
    def query_executor(a: APIFlask, c: ServerCredentials, ttl: int):
        with a.app_context():
            try:
                log_debug('BACKGROUND', 'executing query_bc background task')
                query_all(c, ttl)
            except Exception as e:
                log_error('BACKGROUND', 'Error executing query_bc background task', {
                    'error': str(e),
                    'traceback': traceback.format_exc(),
                })

    # run once a few minutes after the system start
    scheduler.add_job(
        lambda: startup_and_enable_schedule(),
        'date',
        run_date=datetime.now(timezone.utc) + timedelta(seconds=3*TIME_MINUTES),
        misfire_grace_time=None, # type: ignore[arg-type]
        id='query_bc_startup',
    )
