import os
from flask import g

from db.db import DBInterface
from db.mongodb.mongo_db import MyMongoDB
from db.sqlite.sqlite_db import MySQLiteDB


def get_db() -> DBInterface:
    """Get a unique DB instance."""
    db = getattr(g, '_database', None)

    if db is None:
        db_type = os.getenv('APP_DB_TYPE', 'sqlite').lower()
        if db_type == 'mongodb':
            database_name = os.getenv('APP_DB_MONGO_DBNAME', 'proxysg_localdb')
            connection_user = os.getenv('APP_DB_MONGO_CON_USER', 'admin')
            connection_password = os.getenv('APP_DB_MONGO_CON_PASSWORD', 'adminpassword')
            connection_host = os.getenv('APP_DB_MONGO_CON_HOST', 'localhost:27017')
            connection_uri = f"mongodb://{connection_user}:{connection_password}@{connection_host}/"
            db = g._database = MyMongoDB(database_name, connection_uri)
        elif db_type == 'sqlite':
            database_name = os.getenv('APP_DB_SQLITE_FILENAME', './data/mydatabase.db')
            db = g._database = MySQLiteDB(database_name)
        else:
            raise ValueError(f"Unsupported APP_DB_TYPE: {db_type}")

    return db


def close_connection():
    """Remove the current database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
