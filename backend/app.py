import os
import traceback
from os.path import abspath
from typing import Any
from apiflask import APIFlask
from flask import send_from_directory
from flask_compress import Compress
from werkzeug.middleware.proxy_fix import ProxyFix

from db import db_singleton
from background.background_tasks import start_background_tasks
from routes.auth import add_auth_bp
from routes.category import add_category_bp
from routes.compile import add_compile_bp
from routes.history import add_history_bp
from routes.task import add_task_bp
from routes.token import add_token_bp
from routes.url import add_url_bp
from log import setup_logging, log_info, log_error, log_debug

# Initialize APIFlask instead of Flask
app = APIFlask(
    __name__,
    'ProxySG Category Server',
    version='1.1.0',
    docs_path='/docs',
    static_folder='./dist',
)

# add module to allow compression of replies
Compress(app)

# load env variables into app.config
# overwrite the default loads, to keep properties as strings instead of doing a JSON parse
app.config.from_prefixed_env(prefix='APP', loads=lambda x: x)
# we can then use app.config.get('module', {}).get('property', 'default val') to access them
# for an example see the wsgi ProxyFix below

# setup logging
setup_logging(app)

# Fix for src_ip if used behind a reverse Proxy
if app.config.get('PROXY_FIX', 'false').lower() == 'true':
    log_info('APP', 'applying reverse proxy fix')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


# Register blueprints
add_category_bp(app)
add_history_bp(app)
add_auth_bp(app)
add_token_bp(app)
add_url_bp(app)
add_compile_bp(app)
add_task_bp(app)


# Serve index.html for the root route
@app.get('/', defaults={'path': ''})
@app.get('/<path:path>')
def catch_all(path: str):
    """Catch-all route for non-API routes."""
    static_folder = abspath(app.static_folder)
    static_file = os.path.join(static_folder, path)

    # Check if the requested static file exists
    if os.path.isfile(static_file):
        return send_from_directory(static_folder, path)

    # Fallback to serving index.html
    return send_from_directory(static_folder, 'index.html')


# add 'status' and 'status_code' fields to the default flask errors
@app.error_processor
def handle_error(error):
    log_error('APP', 'FLASK Error', {
        'status_code': error.status_code,
        'message': error.message,
        'detail': error.detail,
        'traceback': traceback.format_exc(),
    })
    return {
        'status': 'failed',
        'status_code': error.status_code,
        'message': error.message,
        'detail': error.detail,
    }, error.status_code, error.headers


@app.teardown_appcontext
def teardown(_exception: Any):
    # the exception parameter must be defined, or else Flask crashes
    log_debug("APP", "App teardown called")
    db_singleton.close_connection()


def initialize_app(a: APIFlask):
    log_debug("APP", "App initialization called")
    # force db initialization and therefore also schema migration
    with app.app_context():
        db_singleton.get_db()
    # start background tasks
    start_background_tasks(a)


if __name__ == '__main__':
    # initialize background tasks
    # we keep this in the __main__ and manually trigger it for gunicorn with the on_starting
    # to prevent the background tasks being run on multiple workers
    initialize_app(app)

    # start app
    app_port = int(app.config.get('PORT', 8080))
    app.run(port=app_port, host='0.0.0.0')
