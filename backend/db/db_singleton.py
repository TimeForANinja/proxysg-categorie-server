from db.db import DBInterface
from db.sqlite.sqlite_db import MySQLiteDB
from flask import g


def get_db(database_name='./data/mydatabase.db') -> DBInterface:
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = MySQLiteDB(database_name)

    return db

def close_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
