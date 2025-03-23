import sqlite3

from db.db import DBInterface
from db.sqlite.categories_db import SQLCategories
from db.sqlite.history_db import SQLHistory
from db.sqlite.tokens_db import SQLTokens
from db.sqlite.token_categories_db import SQLTokenCategories
from db.sqlite.urls_db import SQLURLs
from db.sqlite.url_categories_db import SQLURLCategories

class MySQLDB(DBInterface):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename
        self.conn = sqlite3.connect(filename)

        self.categories = SQLCategories(self.conn)
        self.history = SQLHistory(self.conn)
        self.tokens = SQLTokens(self.conn)
        self.token_categories = SQLTokenCategories(self.conn)
        self.urls = SQLURLs(self.conn)
        self.url_categories = SQLURLCategories(self.conn)

    def close(self):
        self.conn.close()
