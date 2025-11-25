"""
Gunicorn Configuration for ProxySG Category Server

This configuration file manages the initialization of background tasks in a multi-worker
Gunicorn deployment. It ensures that background tasks (such as scheduled category syncs)
are started only once across all worker processes, preventing duplicate task execution.
"""

import os
from typing import Any

from app import app, init_background, migrate_db
from log import log_debug

LOCK_FILE = "/tmp/proxysg_background_initialized"


def on_starting(_server: Any):
    """
    Called once when the Gunicorn master process starts.

    Clears any lock file from previous server instances to ensure
    a clean initialization state for the new deployment.

    @param _server: Gunicorn server instance (unused)
    """
    log_debug("APP", "App on_starting called")
    # attempt to clear any lock file from previous starts
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass  # Lock file doesn't exist, that's fine
    log_debug("APP", "App on_starting passed first stage")

    migrate_db(app)
    log_debug("APP", "App on_starting passed second stage")


def post_fork(_server: Any, _worker: Any):
    """
    Called after each worker process is forked from the master.

    Uses atomic file creation to ensure only one worker initializes
    the application and starts background tasks. Other workers skip
    initialization to avoid duplicate task scheduling.

    @param _server: Gunicorn server instance (unused)
    @param _worker: Gunicorn worker instance (unused)
    """
    log_debug("APP", "App post_fork called")
    try:
        # Attempt to create the lock atomically
        # if it exists, another worker already initialized
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)

        # the first worker to acquire the lock starts the background scheduler
        init_background(app)
    except FileExistsError:
        # Another worker has already initialized background tasks
        pass

    # no further task needed - worker starts automatically after this
    pass
