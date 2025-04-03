import os
import urllib3
from datetime import timedelta, datetime
from apiflask import APIFlask
from apscheduler.schedulers.background import BackgroundScheduler

from other.query_bc import ServerCredentials, query_all


def start_background_tasks(app: APIFlask):
    """Initialize all background tasks"""
    start_query_bc(app)


def start_query_bc(app: APIFlask):
    """
    Initialize the background task to query URL Categories from Bluecoat DB
    This is only possible with the Mgmt API of a Proxy Device
    """

    # load required config variables
    bc_interval = os.getenv('APP_BC_INTERVAL', 86400)
    bc_db = os.getenv('APP_BC_DB')
    bc_user = os.getenv('APP_BC_USER', 'ro_admin')
    bc_password = os.getenv('APP_BC_PASSWORD')
    # check for false or not false, so that we default to "true" for all other values
    bc_verify_ssl = os.getenv('APP_BC_VERIFY_SSL', 'true').lower() != "false"

    if not bc_verify_ssl:
        # hide warnings telling us to enable ssl verification
        urllib3.disable_warnings()

    # build credential object to make it easier to pass them around
    creds = ServerCredentials(
        server=bc_db,
        user=bc_user,
        password=bc_password,
        verifySSL=bc_verify_ssl,
    )

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as flask global object
    def query_executor(a: APIFlask, c: ServerCredentials, unknown_only:bool=False):
        with a.app_context():
            query_all(c, unknown_only)

    # Prepare the Scheduler
    scheduler = BackgroundScheduler()

    # run at the interval defined
    # and once "quick" after 1 minute (only query not-yet-rated URLs)
    scheduler.add_job(
        lambda: query_executor(app, creds),
        'interval',
        seconds=int(bc_interval)
    )
    scheduler.add_job(
        lambda: query_executor(app, creds, True),
        'date',
        run_date=datetime.now() + timedelta(seconds=60)
    )

    # Start the Scheduler
    scheduler.start()
