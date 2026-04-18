from flask import current_app
from db.dbm.db import DBMDB
from db.mongo.db import MongoDB
from db.sqlite.db import SQLiteDB
from db.cache.db import CacheDB
from model.model import MyModel
from util.log import log_info, log_debug


def get_db() -> MyModel:
    """
    Singleton factory for the database model.
    Initializes the appropriate database backend based on configuration (DB: TYPE).
    Optionally wraps the backend with a caching layer.

    :return: An initialized instance of MyModel with the configured backend.
    """
    my_model = current_app.config.get('SINGLETONS', {}).get('DB', None)

    if my_model is None:
        log_debug("DB", "Initializing DB connection")
        db_cfg = current_app.config.get('DB', {})

        db_type = db_cfg.get("TYPE", {})
        if not db_type:
            raise ValueError("Environment variable DB__TYPE is not set")

        log_info('DB', f'Initializing {db_type} backend')

        #################
        # Persistent DB #
        #################
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
            username = mongo_cfg.get('USERNAME')
            password = mongo_cfg.get('PASSWORD')
            auth_source = mongo_cfg.get('AUTHSOURCE', mongo_cfg.get('AUTHREALM', database_name))
            connect_direct = mongo_cfg.get('CONNECT_DIRECT', 'false').lower() == 'true'
            collection_name = mongo_cfg.get('COLLECTION', 'data')

            log_info('DB', 'Creating MongoDB DB', {
                'host': host,
                'port': port,
                'db': database_name,
                'user': username,
                'authSource': auth_source,
                'direct': connect_direct
            })
            backend = MongoDB(
                host=host,
                port=port,
                database_name=database_name,
                username=username,
                password=password,
                auth_source=auth_source,
                connect_direct=connect_direct,
                collection_name=collection_name
            )
        elif db_type == 'sqlite':
            sqlite_cfg = db_cfg.get('SQLITE', {})
            database_name = sqlite_cfg.get('FILENAME', './data/mydatabase.sqlite')
            log_info('DB', 'Creating SQLite DB', {'db': database_name})
            backend = SQLiteDB(database_name)
        else:
            raise ValueError(f"Unsupported DB_TYPE: {db_type}")

        ##############################
        # In-Memory Cache Middleware #
        ##############################
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
    Close the current database connection and remove it from the singleton store.
    Flask calls this when the application context is torn down.
    """
    my_model = current_app.config.get('SINGLETONS', {}).get('DB', None)
    if my_model is not None:
        my_model.backend.close()
        current_app.config['SINGLETONS']['DB'] = None
