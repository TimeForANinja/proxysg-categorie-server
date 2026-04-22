from datetime import timedelta, datetime, timezone
from typing import List

from apiflask import APIFlask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from db.db_singleton import get_db
from model.model import MyModel
from model.types.core import Commit
from model.types.url import URL
from model.types.metrics import BCCategory
from util.branch_names import BRANCH_PROD
from util.log import log_debug, log_error_obj


TIME_MINUTES = 60
# Allows up to 15 minutes as a grace period if the Scheduler is busy / blocked by other stuff
MISFIRE_GRACE_TIME = 15 * TIME_MINUTES
# Delay the first query by 5 minutes to allow the system to start up
START_DELAY_MIN = 5 * TIME_MINUTES


def start_background_tasks(app: APIFlask):
    """Initialize all background tasks"""

    # load required config variables
    tz = app.config.get("TIMEZONE", "Europe/Berlin")

    log_debug("BACKGROUND", "Starting Background Tasks...", { "tz": tz })

    # Prepare the Scheduler
    scheduler = BackgroundScheduler({"apscheduler.timezone": tz})

    # add all tasks
    start_query_bc(scheduler, app, tz)

    # Start the Scheduler
    scheduler.start()


def start_query_bc(scheduler: BackgroundScheduler, app: APIFlask, tz: str):
    """
    Initialize the background task to query URL Categories from Bluecoat DB
    This is only possible with the Mgmt API of a Proxy Device

    :param scheduler: The scheduler to use
    :param app: The flask app to use
    :param tz: The timezone to use for cron triggers
    """

    # load required config variables
    query_bc_conf: dict = app.config.get("BC", {})
    bc_interval = query_bc_conf.get("INTERVAL", "0 3 * * *")
    bc_ttl = int(query_bc_conf.get("TTL", 7 * 24 * 60)) * TIME_MINUTES
    log_debug("BACKGROUND", "Preparing Background Tasks 'start_query_bc'", {
        "interval": bc_interval,
        "ttl": bc_ttl,
    })

    def startup_and_enable_schedule():
        # execute the first query
        query_executor(app, bc_ttl)
        # then add the long-terms chedule
        scheduler.add_job(
            lambda: query_executor(app, bc_ttl),
            CronTrigger.from_crontab(bc_interval, timezone=tz),
            misfire_grace_time=MISFIRE_GRACE_TIME,
            id="query_bc_cron",
        )

    # wrapper to use the app_context
    # this allows us to use the existing db_singleton stored as a flask global object
    def query_executor(a: APIFlask, ttl: int):
        with a.app_context():
            try:
                log_debug("BACKGROUND", "executing query_bc background task")
                bc_query_all(get_db(), a, ttl)
            except Exception as e:
                log_error_obj("BACKGROUND", "Error executing query_bc background task", e)

    # run once a few minutes after the system start
    scheduler.add_job(
        lambda: startup_and_enable_schedule(),
        "date",
        run_date=datetime.now(timezone.utc) + timedelta(seconds=START_DELAY_MIN),
        misfire_grace_time=None, # type: ignore[arg-type]
        id="query_bc_startup",
    )


def bc_query_all(db_if: MyModel, app: APIFlask, ttl: int):
    """
    Method to query all URLs in the DB for their BlueCoat Categories

    :param db_if: The DBInterface to use for the DB operations
    :param app: The flask app to use
    :param ttl: The max TTL after which to force-refresh the rating
    """
    c = Commit.read_branch(db_if.backend, BRANCH_PROD)
    urls = URL.batch_read(db_if.backend, c.head.urls)
    current_cats = BCCategory.batch_read_lut(db_if.backend)

    to_update: List[str] = []
    for u in urls:
        # Two conditions two update
        # 1. The category is not in the DB or the TTL is expired
        # 2. The category is in the DB but needs to be refreshed
        if u.id in current_cats and current_cats[u.id].needs_refresh(ttl):
            to_update.append(u.url)
        elif u.id not in current_cats:
            to_update.append(u.url)

    log_debug("background","planning update of BlueCoat categories", {
        "total-urls": len(urls),
        "total-categories": len(current_cats),
        "planned": len(to_update),
    })

    BCCategory.batch_update(db_if.backend, app, to_update)
