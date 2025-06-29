from flask import current_app

from db.backend.mongodb.db import MyMongoDB
from db.backend.sqlite.db import MySQLiteDB
from db.middleware.stagingdb.db import StagingDB
from log import log_info
from pymongo import MongoClient


def get_db() -> StagingDB:
    """Get a unique DB instance."""
    staging_db = current_app.config.get('SINGLETONS', {}).get('DB', None)

    if staging_db is None:
        db_type = current_app.config.get('DB', {}).get('TYPE', 'sqlite').lower()
        if db_type == 'mongodb':
            mongo_cfg: dict = current_app.config.get('DB', {}).get('MONGO', {})
            database_name = mongo_cfg.get('DBNAME', 'proxysg_localdb')
            connection_auth_real = mongo_cfg.get('DBAUTH', database_name)
            connection_user = mongo_cfg.get('CON_USER', 'admin')
            connection_password = mongo_cfg.get('CON_PASSWORD', 'adminpassword')
            connection_host = mongo_cfg.get('CON_HOST', 'localhost')
            connection_port = mongo_cfg.get('CON_PORT', 27017)
            log_info('DB', 'Connecting to MongoDB', { 'db': database_name, 'auth_db': connection_auth_real, 'user': connection_user, 'host': f'{connection_host}:{connection_port}' })
            db = MyMongoDB(MongoClient(
                connection_host,
                connection_port,
                username=connection_user,
                password=connection_password,
                authSource=connection_auth_real
            ), database_name)
        elif db_type == 'sqlite':
            sqlite_cfg: dict = current_app.config.get('DB', {}).get('SQLITE', {})
            database_name = sqlite_cfg.get('APP_DB_SQLITE_FILENAME', './data/mydatabase.db')
            log_info('DB', 'Creating Standby SQLite DB', { 'db': database_name })
            db = MySQLiteDB(database_name)
        else:
            raise ValueError(f'Unsupported APP_DB_TYPE: {db_type}')

        staging_db = StagingDB(db)

        current_app.config.setdefault('SINGLETONS', {})
        current_app.config['SINGLETONS']['DB'] = staging_db

    return staging_db


def close_connection():
    """
    Remove the current database connection.
    Flask calls this every time a Context is being removed (e.g., end of request)
    """
    db = get_db()
    if db is not None:
        db.close()
