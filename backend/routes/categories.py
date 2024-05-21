from flask import Blueprint, jsonify, request
from db.mydb import DatabaseHolder

from db.categories_db import CategoriesDB

categories_bp = Blueprint('categories', __name__)


# Route to fetch all Categories
@categories_bp.route('/categorie', methods=['GET'])
def get_categories():
    conn = DatabaseHolder().mydb.conn
    categories_db = CategoriesDB(conn)
    categories = categories_db.get_all_categories()
    return jsonify(categories)

# Route to update Category name
@categories_bp.route('/categorie/<int:id>', methods=['UPDATE'])
def update_category(id):
    conn = DatabaseHolder().mydb.conn
    categories_db = CategoriesDB(conn)
    category = categories_db.get_category(id)

    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    data = request.json
    new_name = data.get('name')

    if not new_name:
        return jsonify({"error": "Name is required"}), 400

    categories_db.update_category(id, new_name)

    new_category = categories_db.get_category(id)
    return jsonify({
        "message": "Category updated successfully",
        "obj": new_category
    })

# Route to delete a Category
@categories_bp.route('/categorie/<int:id>', methods=['DELETE'])
def delete_category(id):
    conn = DatabaseHolder().mydb.conn
    categories_db = CategoriesDB(conn)
    category = categories_db.get_category(id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    categories_db.delete_category(id)
    return jsonify({"message": "Category deleted successfully"})


# Route to create a new Category
@categories_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = DatabaseHolder().mydb.conn
    categories_db = CategoriesDB(conn)
    new_id = categories_db.add_category(name)

    new_category = categories_db.get_category(new_id)
    return jsonify({
        "message": "Category created successfully",
        "obj": new_category,
    })
