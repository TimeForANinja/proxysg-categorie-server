from flask import Blueprint, jsonify, request
from mydb import MyDB
from url_categories_db import UrlCategoriesDB

url_categories_bp = Blueprint('url_categories', __name__)

# Initialize MyDB with SQLite filename
mydb = MyDB('mydatabase.db')


# Route to get categories for a URL
@url_categories_bp.route('/urls/<int:id>/categories', methods=['GET'])
def get_categories_for_url(id):
    conn = mydb.conn
    url_categories_db = UrlCategoriesDB(conn)
    categories = url_categories_db.get_categories_for_url(id)
    return jsonify(categories)


# Route to add a category to a URL
@url_categories_bp.route('/urls/<int:id>/categories', methods=['POST'])
def add_category_to_url(id):
    data = request.json
    category_id = data.get('category_id')

    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400

    conn = mydb.conn
    url_categories_db = UrlCategoriesDB(conn)
    url_categories_db.add_category_to_url(id, category_id)
    return jsonify({"message": "Category added to URL successfully"})


# Route to remove a category from a URL
@url_categories_bp.route('/urls/<int:id>/categories', methods=['DELETE'])
def remove_category_from_url(id):
    data = request.json
    category_id = data.get('category_id')

    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400

    conn = mydb.conn
    url_categories_db = UrlCategoriesDB(conn)
    url_categories_db.remove_category_from_url(id, category_id)
    return jsonify({"message": "Category removed from URL successfully"})
