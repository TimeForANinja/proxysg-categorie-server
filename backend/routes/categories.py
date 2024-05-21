from flask import Blueprint, jsonify, request
from mydb import MyDB
from categories_db import CategoriesDB

categories_bp = Blueprint('categories', __name__)

# Initialize MyDB with SQLite filename
mydb = MyDB('mydatabase.db')


# Route to fetch all Categories
@categories_bp.route('/categorie', methods=['GET'])
def get_categories():
    conn = mydb.conn
    categories_db = CategoriesDB(conn)
    categories = categories_db.get_all_categories()
    return jsonify(categories)

# Route to update Category name
@categories_bp.route('/categorie/<int:id>', methods=['UPDATE'])
def update_category(id):
    conn = mydb.conn
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
    conn = mydb.conn
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

    conn = mydb.conn
    categories_db = CategoriesDB(conn)
    new_id = categories_db.add_category(name)

    new_category = categories_db.get_category(new_id)
    return jsonify({
        "message": "Category created successfully",
        "obj": new_category,
    })
