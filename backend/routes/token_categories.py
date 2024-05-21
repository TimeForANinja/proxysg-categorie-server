from flask import Blueprint, jsonify, request
from mydb import MyDB
from db.token_categories_db import TokenCategoriesDB

token_categories_bp = Blueprint('token_categories', __name__)

# Initialize MyDB with SQLite filename
mydb = MyDB('mydatabase.db')


# Route to get categories for a Token
@token_categories_bp.route('/tokens/<int:id>/categories', methods=['GET'])
def get_categories_for_token(id):
    conn = mydb.conn
    token_categories_db = TokenCategoriesDB(conn)
    categories = token_categories_db.get_categories_for_token(id)
    return jsonify(categories)


# Route to add a category to a Token
@token_categories_bp.route('/tokens/<int:id>/categories', methods=['POST'])
def add_category_to_token(id):
    data = request.json
    category_id = data.get('category_id')

    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400

    conn = mydb.conn
    token_categories_db = TokenCategoriesDB(conn)
    token_categories_db.add_category_to_token(id, category_id)
    return jsonify({"message": "Category added to Token successfully"})


# Route to remove a category from a Token
@token_categories_bp.route('/tokens/<int:id>/categories', methods=['DELETE'])
def remove_category_from_token(id):
    data = request.json
    category_id = data.get('category_id')

    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400

    conn = mydb.conn
    token_categories_db = TokenCategoriesDB(conn)
    token_categories_db.remove_category_from_token(id, category_id)
    return jsonify({"message": "Category removed from Token successfully"})
