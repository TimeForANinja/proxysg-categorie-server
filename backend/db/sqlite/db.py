import os
import sqlite3
from flask import g

from db.abc.db import DBInterface
from db.sqlite.category_db import SQLiteCategory
from db.sqlite.config_db import SQLiteConfig, CONFIG_VAR_SCHEMA_VERSION
from db.sqlite.history_db import SQLiteHistory
from db.sqlite.staging_db import SQLiteStaging
from db.sqlite.sub_category_db import SQLiteSubCategory
from db.sqlite.token_db import SQLiteToken
from db.sqlite.token_category_db import SQLiteTokenCategory
from db.sqlite.url_db import SQLiteURL
from db.sqlite.url_category_db import SQLiteURLCategory
from log import log_info, log_debug, log_error


class MySQLiteDB(DBInterface):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename

        # Initialize the config table first to manage a schema version
        self.config = SQLiteConfig(self.open_con)

        # Initialize other tables
        self.categories = SQLiteCategory(self.open_con)
        self.sub_categories = SQLiteSubCategory(self.open_con)
        self.history = SQLiteHistory(self.open_con)
        self.tokens = SQLiteToken(self.open_con)
        self.token_categories = SQLiteTokenCategory(self.open_con)
        self.urls = SQLiteURL(self.open_con)
        self.url_categories = SQLiteURLCategory(self.open_con)
        self.staging = SQLiteStaging(self.open_con)

        # Run migrations if needed
        self._run_migrations()

    def open_con(self) -> sqlite3.Connection:
        # helper method to provide access to a sqlite con for other SQLite Modules
        # we unfortunately need to open the connection new for each threat...
        # flask 'g' is unique for each context, so we can use it to store the connection
        conn = getattr(g, '_sqlite_db', None)
        if conn is None:
            conn = g._sqlite_db = sqlite3.connect(self.filename)
        return conn

    def close(self):
        # close the sqlite connection after each request
        # this is required, since flask creates new threads for each request
        # and each request requires its own DB instance
        conn = getattr(g, '_sqlite_db', None)
        if conn is not None:
            conn.close()

    def _run_migrations(self):
        """
        Check for migration scripts and run them in sequence to upgrade the database schema.
        Migration scripts should be named in the format: <version>_<description>.sql
        """
        # Get current schema version
        current_version = self.config.get_schema_version()
        log_debug('SQLITE', f'Current schema version: {current_version}')

        # Find migration scripts
        migration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migration')
        os.makedirs(migration_dir, exist_ok=True)  # Ensure migration directory exists

        # Get all SQL files in the migration directory
        migration_files = []
        for file in os.listdir(migration_dir):
            if file.endswith('.sql'):
                try:
                    # Extract version number from filename (format: <version>_<description>.sql)
                    version = int(file.split('_')[0])
                    migration_files.append((version, os.path.join(migration_dir, file)))
                except (ValueError, IndexError):
                    # Skip files that don't follow the naming convention
                    log_error("SQLITE", f"Skipping invalid migration file: {file}")
                    continue

        # Sort migration files by version
        migration_files.sort(key=lambda x: x[0])

        # Run migrations that are newer than the current version
        conn = self.open_con()
        cursor = conn.cursor()

        for version, file_path in migration_files:
            if version > current_version:
                log_debug("SQLITE", f"Applying migration: {os.path.basename(file_path)}")
                try:
                    # Read and execute the migration script
                    with open(file_path, 'r') as f:
                        sql_script = f.read()

                    # Execute the script
                    # use BEGIN/COMMIT to enforce a transaction - changes are only stored if all changes succeed
                    cursor.executescript(f"BEGIN;\n{ sql_script }\nCOMMIT;")
                    conn.commit()

                    # Update schema version
                    self.config.set_int(CONFIG_VAR_SCHEMA_VERSION, version)

                    log_info("SQLITE", f"Applied migration: {os.path.basename(file_path)}")
                except Exception as e:
                    conn.rollback()
                    log_error("SQLITE", f"Error applying migration {os.path.basename(file_path)}: {str(e)}")
                    # migration failed
                    # raise to stop the server since the DB is not as expected
                    raise e
            else:
                log_debug("SQLITE", f"Skipping migration: {os.path.basename(file_path)} (version {version} is older than current version {current_version})")
