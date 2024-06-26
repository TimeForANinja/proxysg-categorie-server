class UrlsDB:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            is_deleted INTEGER NOT NULL DEFAULT 0
                        )''')
        self.conn.commit()

    def add_url(self, name):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO urls (name) VALUES (?)', (name,))
        self.conn.commit()
        return cursor.lastrowid

    def get_url(self, url_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM urls WHERE id = ? AND is_deleted = 0', (url_id,))
        return cursor.fetchone()

    def update_url(self, url_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE urls SET name = ? WHERE id = ? AND is_deleted = 0', (new_name, url_id))
        self.conn.commit()

    def delete_url(self, url_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE urls SET is_deleted = 1 WHERE id = ?', (url_id,))
        self.conn.commit()

    def get_all_urls(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM urls WHERE is_deleted = 0')
        return cursor.fetchall()
