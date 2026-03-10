from flask import current_app

from db.backend.sqlite.db import MySQLiteDB
from db.middleware.abc.db import MiddlewareDB
from db.middleware.stagingdb.db import StagingDB
from log import log_info, log_debug


def get_db() -> MiddlewareDB:
    """Get a unique DB instance."""
    staging_db = current_app.config.get('SINGLETONS', {}).get('DB', None)

    if staging_db is None:
        log_debug("DB", "Initializing DB connection", current_app.config.get('DB', {}))
        db_type = current_app.config.get('DB', {}).get('TYPE', 'sqlite').lower()
        if db_type == 'sqlite':
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
    db = current_app.config.get('SINGLETONS', {}).get('DB', None)
    if db is not None:
        db.close()
        current_app.config['SINGLETONS']['DB'] = None
