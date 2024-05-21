import sqlite3

class CategoriesDB:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL
                        )''')
        self.conn.commit()

    def add_category(self, name):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        self.conn.commit()
        return cursor.lastrowid

    def get_category(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
        return cursor.fetchone()

    def update_category(self, category_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, category_id))
        self.conn.commit()

    def delete_category(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        self.conn.commit()

    def get_all_categories(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM categories')
        return cursor.fetchall()
