import os
from os.path import abspath
from pathlib import Path

from apiflask import APIFlask
from flask import send_from_directory
from flask_compress import Compress

from db import db_singleton
from db.sqlite.sqlite_db import MySQLiteDB
from routes.auth import auth_bp
from routes.category import category_bp
from routes.compile import compile_bp
from routes.history import history_bp
from routes.load_existing import other_bp, parse_db, create_in_db
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


if __name__ == '__main__':
    # load local db if it exists
    existing_local_db = Path("./data/local_db.txt")
    if existing_local_db.is_file():
        file_str = existing_local_db.read_text()
        db = MySQLiteDB('./data/mydatabase.db')
        new_cats = parse_db(file_str)
        create_in_db(db, new_cats)

    # start app
    app_port = int(os.getenv('APP_PORT', 8080))
    app.run(port=app_port, host="0.0.0.0")
