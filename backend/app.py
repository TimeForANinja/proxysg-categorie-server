from apiflask import APIFlask

from db import db_singleton
from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.history import history_bp
from routes.tokens import tokens_bp
from routes.urls import urls_bp

# Initialize APIFlask instead of Flask
app = APIFlask(__name__, "ProxySG Category Server", version="1.0.0", docs_path="/docs")

# Register blueprints
app.register_blueprint(categories_bp)
app.register_blueprint(history_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(tokens_bp)
app.register_blueprint(urls_bp)


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
    app.run(port=8080, host="0.0.0.0")
