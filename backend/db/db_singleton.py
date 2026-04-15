import os
from flask import current_app
from db.dbm.db import DBMDB
from db.mongo.db import MongoDB
from db.cache.db import CacheDB
from model.model import MyModel
from log import log_info, log_debug


def get_db() -> MyModel:
    """Get a unique DB instance."""
    my_model = current_app.config.get('SINGLETONS', {}).get('DB', None)

    if my_model is None:
        log_debug("DB", "Initializing DB connection")
        db_cfg = current_app.config.get('DB', {})

        db_type = db_cfg.get("TYPE", {})
        if not db_type:
            raise ValueError("Environment variable DB__TYPE is not set")

        log_info('DB', f'Initializing {db_type} backend')

        if db_type == 'dbm':
            dbm_cfg = db_cfg.get('DBM', {})
            database_name = dbm_cfg.get('FILENAME', './data/mydatabase.db')
            log_info('DB', 'Creating DBM DB', {'db': database_name})
            backend = DBMDB(database_name)
        elif db_type == 'mongo':
            mongo_cfg = db_cfg.get('MONGO', {})
            host = mongo_cfg.get('HOST', 'localhost')
            port = int(mongo_cfg.get('PORT', 27017))
            database_name = mongo_cfg.get('DATABASE', 'proxysg')
            collection_name = mongo_cfg.get('COLLECTION', 'data')
            log_info('DB', 'Creating MongoDB DB', {'host': host, 'port': port, 'db': database_name})
            backend = MongoDB(host, port, database_name, collection_name)
        else:
            raise ValueError(f"Unsupported DB_TYPE: {db_type}")

        # wrap with cache
        cache_disabled = db_cfg.get('CACHE_DISABLED', 'false').lower() == 'true'
        if not cache_disabled:
            log_info('DB', 'Enabling cache')
            backend = CacheDB(backend)
        else:
            log_info('DB', 'Cache is disabled')

        my_model = MyModel(backend)

        current_app.config.setdefault('SINGLETONS', {})
        current_app.config['SINGLETONS']['DB'] = my_model

    return my_model


def close_connection():
    """
    Remove the current database connection.
    Flask calls this every time a Context is being removed (e.g., end of request)
    """
    my_model = current_app.config.get('SINGLETONS', {}).get('DB', None)
    if my_model is not None:
        my_model.backend.close()
        current_app.config['SINGLETONS']['DB'] = None
