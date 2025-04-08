import sqlite3

from db.db import DBInterface
from db.sqlite.category_db import SQLiteCategory
from db.sqlite.history_db import SQLiteHistory
from db.sqlite.sub_category_db import SQLiteSubCategory
from db.sqlite.token_db import SQLiteToken
from db.sqlite.token_category_db import SQLiteTokenCategory
from db.sqlite.url_db import SQLiteURL
from db.sqlite.url_category_db import SQLiteURLCategory


class MySQLiteDB(DBInterface):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename
        self.conn = sqlite3.connect(filename)

        self.categories = SQLiteCategory(self.conn)
        self.sub_categories = SQLiteSubCategory(self.conn)
        self.history = SQLiteHistory(self.conn)
        self.tokens = SQLiteToken(self.conn)
        self.token_categories = SQLiteTokenCategory(self.conn)
        self.urls = SQLiteURL(self.conn)
        self.url_categories = SQLiteURLCategory(self.conn)

    def close(self):
        self.conn.close()
