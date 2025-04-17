import sqlite3
from typing import Optional
from flask import g

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

        self.categories = SQLiteCategory(self.open_con)
        self.sub_categories = SQLiteSubCategory(self.open_con)
        self.history = SQLiteHistory(self.open_con)
        self.tokens = SQLiteToken(self.open_con)
        self.token_categories = SQLiteTokenCategory(self.open_con)
        self.urls = SQLiteURL(self.open_con)
        self.url_categories = SQLiteURLCategory(self.open_con)

    def open_con(self) -> sqlite3.Connection:
        # helper method to provide a sqlite con for a SQLite Module
        # we unfortunately need to open the connection new for each threat...
        # flask "g" is unique for each context, so we can use it to store the connection
        conn = getattr(g, '_sqlite_db', None)
        if conn is None:
            conn = g._sqlite_db = sqlite3.connect(self.filename)
        return conn

    def close(self):
        # close the sqlite connection after each request
        # this is required, since flask creates new threads for each request
        # and each request requires it's own DB instance
        conn = getattr(g, '_sqlite_db', None)
        if conn is not None:
            conn.close()
