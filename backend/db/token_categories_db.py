class TokenCategoriesDB:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS token_categories (
                            token_id INTEGER,
                            category_id INTEGER,
                            is_deleted INTEGER DEFAULT 0,
                            FOREIGN KEY (token_id) REFERENCES tokens(id),
                            FOREIGN KEY (category_id) REFERENCES categories(id),
                            PRIMARY KEY (token_id, category_id)
                        )''')
        self.conn.commit()

    def add_category_to_token(self, token_id, category_id):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO token_categories (token_id, category_id, is_deleted) VALUES (?, ?, 0)',
                       (token_id, category_id))
        self.conn.commit()

    def remove_category_from_token(self, token_id, category_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE token_categories SET is_deleted = 1 WHERE token_id = ? AND category_id = ?',
                       (token_id, category_id))
        self.conn.commit()

    def get_categories_for_token(self, token_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT category_id FROM token_categories WHERE token_id = ? AND is_deleted = 0', (token_id,))
        return cursor.fetchall()
