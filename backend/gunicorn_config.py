from typing import Any
from app import initialize_app, app

def on_starting(_server: Any):
    # the server parameter must be defined, or else gunicorn crashes

    # Call initialize_app to trigger background tasks scheduler
    # this will only get called for the master worker
    initialize_app(app)
