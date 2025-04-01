import os
from flask import g

from db.db import DBInterface
from db.mongodb.mongo_db import MyMongoDB
from db.sqlite.sqlite_db import MySQLiteDB


def get_db() -> DBInterface:
    db = getattr(g, '_database', None)

    if db is None:
        db_type = os.getenv('APP_DB_TYPE', 'sqlite').lower()  # Default to SQLite
        # TODO: document all ENV variables
        if db_type == 'mongo':
            database_name = os.getenv('APP_DB_MONGO_DBNAME', 'proxysg_localdb')
            connection_uri = os.getenv('APP_DB_MONGO_CON_URL', 'mongodb://admin:adminpassword@localhost:27017/')
            db = g._database = MyMongoDB(database_name, connection_uri)
        elif db_type == 'sqlite':
            database_name = os.getenv('APP_DB_SQLITE_FILENAME', './data/mydatabase.db')
            db = g._database = MySQLiteDB(database_name)
        else:
            raise ValueError(f"Unsupported APP_DB_TYPE: {db_type}")

    return db


def close_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
