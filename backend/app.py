from flask import Flask
from routes.categories import categories_bp
from routes.tokens import tokens_bp
from routes.urls import urls_bp
from routes.token_categories import token_categories_bp
from routes.url_categories import url_categories_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(categories_bp)
app.register_blueprint(tokens_bp)
app.register_blueprint(urls_bp)
app.register_blueprint(token_categories_bp)
app.register_blueprint(url_categories_bp)

if __name__ == '__main__':
    app.run(debug=True)
