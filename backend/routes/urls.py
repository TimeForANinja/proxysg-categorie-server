from flask import Blueprint, jsonify, request
from db.mydb import DatabaseHolder
from db.urls_db import UrlsDB

urls_bp = Blueprint('urls', __name__)


# Route to fetch all URLs
@urls_bp.route('/urls', methods=['GET'])
def get_urls():
    conn = DatabaseHolder().mydb.conn
    urls_db = UrlsDB(conn)
    urls = urls_db.get_all_urls()
    return jsonify(urls)


# Route to update URL name
@urls_bp.route('/urls/<int:id>', methods=['PUT'])
def update_url(id):
    conn = DatabaseHolder().mydb.conn
    urls_db = UrlsDB(conn)
    url = urls_db.get_url(id)

    if not url:
        return jsonify({"error": "URL not found"}), 404
    
    data = request.json
    new_name = data.get('name')

    if not new_name:
        return jsonify({"error": "Name is required"}), 400

    urls_db.update_url(id, new_name)

    new_url = urls_db.get_url(id)
    return jsonify({
        "message": "URL updated successfully",
        "obj": new_url,
    })


# Route to delete a URL
@urls_bp.route('/urls/<int:id>', methods=['DELETE'])
def delete_url(id):
    conn = DatabaseHolder().mydb.conn
    urls_db = UrlsDB(conn)
    url = urls_db.get_url(id)

    if not url:
        return jsonify({"error": "URL not found"}), 404

    urls_db.delete_url(id)
    return jsonify({"message": "URL deleted successfully"})


# Route to create a new URL
@urls_bp.route('/urls', methods=['POST'])
def create_url():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = DatabaseHolder().mydb.conn
    urls_db = UrlsDB(conn)
    new_id = urls_db.add_url(name)
    
    new_url = urls_db.get_url(new_id)
    return jsonify({
        "message": "URL created successfully",
        "obj": new_url,
    })


# Route to fetch all URLs with associated categories
@urls_bp.route('/urls-with-categories', methods=['GET'])
def get_urls_with_categories():
    conn = DatabaseHolder().mydb.conn
    cursor = conn.cursor()

    # Join urls, url_categories, and categories tables to fetch the required data
    cursor.execute('''SELECT urls.id AS url_id, urls.name AS url_name,
                              categories.id AS category_id, categories.name AS category_name
                      FROM urls
                      LEFT JOIN url_categories ON urls.id = url_categories.url_id
                      LEFT JOIN categories ON url_categories.category_id = categories.id''')

    urls_with_categories = {}
    for row in cursor.fetchall():
        url_id, url_name, category_id, category_name = row
        if url_id not in urls_with_categories:
            urls_with_categories[url_id] = {"id": url_id, "name": url_name, "categories": []}

        # Check if category_id is None (no category assigned)
        if category_id is not None:
            urls_with_categories[url_id]["categories"].append({"id": category_id, "name": category_name})

    return jsonify(list(urls_with_categories.values()))
