import sqlite3


class DatabaseHolder:
    _instance = None

    def __new__(cls, database_name='mydatabase.db'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.mydb = MyDB(database_name)
        return cls._instance


class MyDB:
    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
