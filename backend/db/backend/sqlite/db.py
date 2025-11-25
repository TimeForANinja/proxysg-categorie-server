import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

from db.backend.abc.db import DBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.category_db import SQLiteCategory
from db.backend.sqlite.config_db import SQLiteConfig, CONFIG_VAR_SCHEMA_VERSION
from db.backend.sqlite.history_db import SQLiteHistory
from db.backend.sqlite.staging_db import SQLiteStaging
from db.backend.sqlite.sub_category_db import SQLiteSubCategory
from db.backend.sqlite.task_db import SQLiteTask
from db.backend.sqlite.token_category_db import SQLiteTokenCategory
from db.backend.sqlite.token_db import SQLiteToken
from db.backend.sqlite.url_category_db import SQLiteURLCategory
from db.backend.sqlite.url_db import SQLiteURL
from log import log_info, log_debug, log_error


class MySQLiteDB(DBInterface):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename

        # Initialize the config table first to manage a schema version
        self.config = SQLiteConfig(self.get_cursor)

        # Initialize other tables
        self.categories = SQLiteCategory(self.get_cursor)
        self.sub_categories = SQLiteSubCategory(self.get_cursor)
        self.history = SQLiteHistory(self.get_cursor)
        self.tokens = SQLiteToken(self.get_cursor)
        self.token_categories = SQLiteTokenCategory(self.get_cursor)
        self.urls = SQLiteURL(self.get_cursor)
        self.url_categories = SQLiteURLCategory(self.get_cursor)
        self.tasks = SQLiteTask(self.get_cursor)
        self.staging = SQLiteStaging(self.get_cursor)

    @contextmanager
    def get_connection(self, session: Optional[MyTransactionType] = None) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager that provides a connection and automatically handles cleanup.

        Usage:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM table')
                result = cursor.fetchall()
        """
        if session is not None:
            # if we're given a session (open transaction), use it
            yield session
            return

        with sqlite3.connect(self.filename) as conn:
            yield conn
            # this will auto-commit when exiting the with block

    @contextmanager
    def get_cursor(self, session: Optional[MyTransactionType] = None) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager that provides a cursor and automatically handles connection cleanup.

        Usage:
            with self.get_cursor() as cursor:
                cursor.execute('SELECT * FROM table')
                result = cursor.fetchall()
        """
        with self.get_connection(session=session) as conn:
            yield conn.cursor()

    def close(self):
        # sqlite is never permanently open - so nothing to do here
        pass

    def migrate(self):
        """
        Run Initialization and Optimization steps.
        Check for migration scripts and run them in sequence to upgrade the database schema.
        Migration scripts should be named in the format: <version>_<description>.sql
        """
        # Get current schema version
        current_version = self.config.get_schema_version()
        log_info('SQLITE', f'Current schema version: {current_version}')

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
        for version, file_path in migration_files:
            if version <= current_version:
                log_debug('SQLITE', f"Skipping migration: {os.path.basename(file_path)} (version {version} is older or equal to current version {current_version})")
                continue

            log_debug("SQLITE", f"Applying migration: {os.path.basename(file_path)}")
            try:
                # Read and execute the migration script
                with open(file_path, 'r') as f:
                    sql_script = f.read()

                with self.start_transaction() as session:
                    with self.get_cursor(session=session) as cursor:
                        # Execute the script
                        # use BEGIN/COMMIT to enforce a transaction - changes are only stored if all changes succeed
                        cursor.executescript(f"BEGIN;\n{sql_script};")
                    # Update schema version, as part of the same transaction
                    self.config.set_int(CONFIG_VAR_SCHEMA_VERSION, version, session=session)
                    # leave the with block to commit the transaction

                log_info("SQLITE", f"Applied migration: {os.path.basename(file_path)}")
            except Exception as e:
                log_error("SQLITE", f"Error applying migration {os.path.basename(file_path)}: {str(e)}")
                # migration failed
                # raise to stop the server since the DB is not as expected
                raise e

    @contextmanager
    def start_transaction(self) -> Generator[MyTransactionType, None, None]:
        # for a sqlite transaction it's only required to reuse the same connection
        # commit / rollback is automatically handled when the with block is exited
        with self.get_connection(session=None) as conn:
            yield conn
