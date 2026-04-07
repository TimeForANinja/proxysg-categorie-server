from flask import current_app
from db.dbm.db import DBM_DB
from model.model import MyModel
from log import log_info, log_debug

def get_db() -> MyModel:
    """Get a unique DB instance."""
    my_model = current_app.config.get('SINGLETONS', {}).get('DB', None)

    if my_model is None:
        log_debug("DB", "Initializing DB connection")
        db_cfg = current_app.config.get('DB', {})
        dbm_cfg = db_cfg.get('DBM', {})
        database_name = dbm_cfg.get('FILENAME', './data/mydatabase.db')
        
        log_info('DB', 'Creating DBM DB', {'db': database_name})
        backend = DBM_DB(database_name)
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
