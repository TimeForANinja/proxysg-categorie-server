class UrlCategoriesDB:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS url_categories (
                            url_id INTEGER,
                            category_id INTEGER,
                            FOREIGN KEY (url_id) REFERENCES urls(id),
                            FOREIGN KEY (category_id) REFERENCES categories(id),
                            PRIMARY KEY (url_id, category_id)
                        )''')
        self.conn.commit()

    def add_category_to_url(self, url_id, category_id):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO url_categories (url_id, category_id) VALUES (?, ?)', (url_id, category_id))
        self.conn.commit()

    def remove_category_from_url(self, url_id, category_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM url_categories WHERE url_id = ? AND category_id = ?', (url_id, category_id))
        self.conn.commit()

    def get_categories_for_url(self, url_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT category_id FROM url_categories WHERE url_id = ?', (url_id,))
        return cursor.fetchall()
