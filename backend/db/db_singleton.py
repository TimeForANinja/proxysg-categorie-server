from flask import current_app

from db.db import DBInterface
from db.mongodb.mongo_db import MyMongoDB
from db.sqlite.sqlite_db import MySQLiteDB
from log import log_info


def get_db() -> DBInterface:
    """Get a unique DB instance."""
    db = current_app.config.get('SINGLETONS', {}).get('DB', None)

    if db is None:
        db_type = current_app.config.get('DB', {}).get('TYPE', 'sqlite').lower()
        if db_type == 'mongodb':
            mongo_cfg: dict = current_app.config.get('DB', {}).get('MONGO', {})
            database_name = mongo_cfg.get('DBNAME', 'proxysg_localdb')
            connection_user = mongo_cfg.get('CON_USER', 'admin')
            connection_password = mongo_cfg.get('CON_PASSWORD', 'adminpassword')
            connection_host = mongo_cfg.get('CON_HOST', 'localhost:27017')
            connection_uri = f'mongodb://{connection_user}:{connection_password}@{connection_host}/?authSource={database_name}'
            log_info('DB', 'Connecting to MongoDB', { 'db': database_name, 'user': connection_user, 'host': connection_host })
            db = MyMongoDB(database_name, connection_uri)
        elif db_type == 'sqlite':
            sqlite_cfg: dict = current_app.config.get('DB', {}).get('SQLITE', {})
            database_name = sqlite_cfg.get('APP_DB_SQLITE_FILENAME', './data/mydatabase.db')
            log_info('DB', 'Creating Standby SQLite DB', { 'db': database_name })
            db = MySQLiteDB(database_name)
        else:
            raise ValueError(f'Unsupported APP_DB_TYPE: {db_type}')

        current_app.config.setdefault('SINGLETONS', {})
        current_app.config['SINGLETONS']['DB'] = db

    return db


def close_connection():
    """
    Remove the current database connection.
    Flask calls this every time a Context is being removed (e.g., end of request)
    """
    db = get_db()
    if db is not None:
        db.close()
