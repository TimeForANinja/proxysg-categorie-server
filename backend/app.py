import os
from os.path import abspath
from apiflask import APIFlask
from flask import send_from_directory
from flask_compress import Compress

from db import db_singleton
from other.background_tasks import start_background_tasks
from routes.auth import auth_bp
from routes.category import category_bp
from routes.compile import compile_bp
from routes.history import history_bp
from routes.load_existing import other_bp
from routes.token import token_bp
from routes.url import url_bp

# Initialize APIFlask instead of Flask
app = APIFlask(
    __name__,
    "ProxySG Category Server",
    version="1.0.0",
    docs_path="/docs",
    static_folder="./dist",
)
Compress(app)

# Register blueprints
app.register_blueprint(category_bp)
app.register_blueprint(history_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(token_bp)
app.register_blueprint(url_bp)
app.register_blueprint(compile_bp)
app.register_blueprint(other_bp)


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


# add "status" and "status_code" fields to the default flask errors
@app.error_processor
def handle_error(error):
    return {
        'status': 'failed',
        'status_code': error.status_code,
        'message': error.message,
        'detail': error.detail
    }, error.status_code, error.headers


@app.teardown_appcontext
def teardown(exception):
    db_singleton.close_connection()


def initialize_app(a: APIFlask):
    # start background tasks
    start_background_tasks(a)

if __name__ == '__main__':
    # initialize background tasks
    # we keep this in the __main__ and manually trigger it for gunicorn with the on_starting
    # to prevent the background tasks being run on multiple workers
    initialize_app(app)

    # start app
    app_port = int(os.getenv('APP_PORT', 8080))
    app.run(port=app_port, host="0.0.0.0")
