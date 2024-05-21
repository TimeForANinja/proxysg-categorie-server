from flask import Blueprint, jsonify, request
from mydb import MyDB
from tokens_db import TokensDB

tokens_bp = Blueprint('tokens', __name__)

# Initialize MyDB with SQLite filename
mydb = MyDB('mydatabase.db')


# Route to fetch all Tokens
@tokens_bp.route('/tokens', methods=['GET'])
def get_tokens():
    conn = mydb.conn
    tokens_db = TokensDB(conn)
    tokens = tokens_db.get_all_tokens()
    return jsonify(tokens)


# Route to update Token name
@tokens_bp.route('/tokens/<int:id>', methods=['PUT'])
def update_token(id):
    conn = mydb.conn
    tokens_db = TokensDB(conn)
    token = tokens_db.get_token(id)

    if not token:
        return jsonify({"error": "Token not found"}), 404
    
    data = request.json
    new_name = data.get('name')

    if not new_name:
        return jsonify({"error": "Name is required"}), 400

    tokens_db.update_token(id, new_name)

    new_token = tokens_db.get_token(id)
    return jsonify({
        "message": "Token name updated successfully",
        "obj": new_token,
    })


# Route to delete a Token
@tokens_bp.route('/tokens/<int:id>', methods=['DELETE'])
def delete_token(id):
    conn = mydb.conn
    tokens_db = TokensDB(conn)
    token = tokens_db.get_token(id)

    if not token:
        return jsonify({"error": "Token not found"}), 404

    tokens_db.delete_token(id)
    return jsonify({"message": "Token deleted successfully"})


# Route to create a new Token
@tokens_bp.route('/tokens', methods=['POST'])
def create_token():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = mydb.conn
    tokens_db = TokensDB(conn)
    new_id = tokens_db.add_token(name)

    new_token = tokens_db.get_token(new_id)
    return jsonify({
        "message": "Token created successfully",
        "obj": new_token,
    })


# Route to fetch all Tokens with associated categories
@tokens_bp.route('/tokens-with-categories', methods=['GET'])
def get_tokens_with_categories():
    conn = mydb.conn
    cursor = conn.cursor()

    # Join tokens, token_categories, and categories tables to fetch the required data
    cursor.execute('''SELECT tokens.id AS token_id, tokens.name AS token_name,
                              categories.id AS category_id, categories.name AS category_name
                      FROM tokens
                      LEFT JOIN token_categories ON tokens.id = token_categories.token_id
                      LEFT JOIN categories ON token_categories.category_id = categories.id''')

    tokens_with_categories = {}
    for row in cursor.fetchall():
        token_id, token_name, category_id, category_name = row
        if token_id not in tokens_with_categories:
            tokens_with_categories[token_id] = {"id": token_id, "name": token_name, "categories": []}

        # Check if category_id is None (no category assigned)
        if category_id is not None:
            tokens_with_categories[token_id]["categories"].append({"id": category_id, "name": category_name})

    return jsonify(list(tokens_with_categories.values()))
