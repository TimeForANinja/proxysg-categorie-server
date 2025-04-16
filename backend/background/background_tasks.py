import urllib3
from datetime import timedelta, datetime, timezone
from apiflask import APIFlask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from background.query_bc import ServerCredentials, query_all
from background.load_existing_db import load_existing_file

TIME_MINUTES = 60

# Allows up to 15 minutes as a grace period if the Scheduler is busy / blocked by other stuff
MISFIRE_GRACE_TIME = 15 * TIME_MINUTES


def start_background_tasks(app: APIFlask):
    """Initialize all background tasks"""
    # Prepare the Scheduler
    tz = app.config.get('TIMEZONE', 'Europe/Berlin')
    scheduler = BackgroundScheduler({'apscheduler.timezone': tz})

    # add all tasks
    start_query_bc(scheduler, app, tz)
    start_load_existing(scheduler, app)

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

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as a flask global object
    def query_executor(a: APIFlask):
        with a.app_context():
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
    bc_db = query_bc_conf.get('HOST')
    bc_user = query_bc_conf.get('USER', 'ro_admin')
    bc_password = query_bc_conf.get('PASSWORD')
    # check for false or not false, so that we default to 'true' for all other values
    bc_verify_ssl = query_bc_conf.get('VERIFY_SSL', 'true').lower() != 'false'

    if not bc_verify_ssl:
        # hide warnings telling us to enable ssl verification
        urllib3.disable_warnings()

    # build a credential object to make it easier to pass them around
    creds = ServerCredentials(
        server=bc_db,
        user=bc_user,
        password=bc_password,
        verifySSL=bc_verify_ssl,
    )

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as a flask global object
    def query_executor(a: APIFlask, c: ServerCredentials, unknown_only:bool=False):
        with a.app_context():
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
