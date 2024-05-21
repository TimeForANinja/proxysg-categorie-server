import base64
import secrets


class TokensDB:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            token TEXT NOT NULL UNIQUE
                        )''')
        self.conn.commit()

    def generate_token(self):
        return base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')

    def add_token(self, name):
        token = self.generate_token()
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO tokens (name, token) VALUES (?, ?)', (name, token))
        self.conn.commit()
        return cursor.lastrowid

    def get_token(self, token_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tokens WHERE id = ?', (token_id,))
        return cursor.fetchone()

    def delete_token(self, token_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tokens WHERE id = ?', (token_id,))
        self.conn.commit()

    def get_all_tokens(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tokens')
        return cursor.fetchall()
