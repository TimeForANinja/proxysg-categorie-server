import urllib3
from datetime import timedelta, datetime, timezone
from apiflask import APIFlask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from background.query_bc import ServerCredentials, query_all
from background.load_existing_db import load_existing_file
from background.tasks import execute_load_existing_task
from db.db_singleton import get_db
from log import log_debug

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
            log_debug('BACKGROUND', 'executing load_existing background task')
            load_existing_file(
                filepath=load_existing_path,
                prefix_cats=load_existing_prefix,
            )

    # run once 'quick' after 1 minute
    scheduler.add_job(
        lambda: query_executor(app),
        'date',
        run_date=datetime.now(timezone.utc) + timedelta(seconds=1*TIME_MINUTES),
        misfire_grace_time=MISFIRE_GRACE_TIME,
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
            log_debug('BACKGROUND', 'executing task_scheduler background task')
            db_if = get_db()

            # try to fetch the next pending task from the DB
            task = db_if.tasks.get_next_pending_task()
            if not task:
                return

            match task.name:
                case 'load_existing':
                    execute_load_existing_task(db_if, task)
                case _:
                    log_debug('BACKGROUND', f'Unknown task type: {task.name} in task {task.id}')
                    db_if.tasks.update_task_status(task.id, 'unknown')

    # run every 30 seconds
    scheduler.add_job(
        lambda: task_executor(app),
        'interval',
        seconds=30,
        misfire_grace_time=MISFIRE_GRACE_TIME,
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
    bc_interval_quick = query_bc_conf.get('INTERVAL_QUICK', '0 * * * *')
    bc_host = query_bc_conf.get('HOST')
    bc_user = query_bc_conf.get('USER', 'ro_admin')
    bc_password = query_bc_conf.get('PASSWORD')
    # check for false or not false, so that we default to 'true' for all other values
    bc_verify_ssl = query_bc_conf.get('VERIFY_SSL', 'true').lower() != 'false'

    log_debug('BACKGROUND', 'Preparing Background Tasks "start_query_bc"', {
        'interval': bc_interval,
        'interval_quick': bc_interval_quick,
        'host': bc_host,
        'user': bc_user,
        'verify_ssl': bc_verify_ssl,
    })

    if not bc_verify_ssl:
        # hide warnings telling us to enable ssl verification
        urllib3.disable_warnings()

    # build a credential object to make it easier to pass them around
    creds = ServerCredentials(
        server=bc_host,
        user=bc_user,
        password=bc_password,
        verifySSL=bc_verify_ssl,
    )

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as a flask global object
    def query_executor(a: APIFlask, c: ServerCredentials, unknown_only:bool=False):
        with a.app_context():
            log_debug('BACKGROUND', 'executing query_bc background task', { 'unknown_only': unknown_only })
            query_all(c, unknown_only)

    # run at the interval defined
    # and once 'quick' after 2 minutes (only query not-yet-rated URLs)
    scheduler.add_job(
        lambda: query_executor(app, creds),
        CronTrigger.from_crontab(bc_interval, timezone=tz),
        misfire_grace_time=MISFIRE_GRACE_TIME,
    )
    scheduler.add_job(
        lambda: query_executor(app, creds, True),
        CronTrigger.from_crontab(bc_interval_quick, timezone=tz),
        misfire_grace_time=MISFIRE_GRACE_TIME,
    )
    scheduler.add_job(
        lambda: query_executor(app, creds, True),
        'date',
        run_date=datetime.now(timezone.utc) + timedelta(seconds=3*TIME_MINUTES),
        misfire_grace_time=MISFIRE_GRACE_TIME,
    )
