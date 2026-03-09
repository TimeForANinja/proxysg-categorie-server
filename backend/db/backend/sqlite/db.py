import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

from db.backend.abc.db import DBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.sqlite.category_db import SQLiteCategory
from db.backend.sqlite.git_tree_db import SQLiteTags, SQLiteTaskSet, SQLiteTokenSet, SQLiteURLSet
from db.backend.sqlite.sub_category_db import SQLiteSubCategory
from db.backend.sqlite.task_db import SQLiteTask
from db.backend.sqlite.token_category_db import SQLiteTokenCategory
from db.backend.sqlite.token_db import SQLiteToken
from db.backend.sqlite.url_category_db import SQLiteURLCategory
from db.backend.sqlite.url_db import SQLiteURL
from log import log_info, log_error


class MySQLiteDB(DBInterface):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename

        # Initialize tables
        self.categories = SQLiteCategory(self.get_cursor)
        self.sub_categories = SQLiteSubCategory(self.get_cursor)
        self.tokens = SQLiteToken(self.get_cursor)
        self.token_categories = SQLiteTokenCategory(self.get_cursor)
        self.urls = SQLiteURL(self.get_cursor)
        self.url_categories = SQLiteURLCategory(self.get_cursor)
        self.tasks = SQLiteTask(self.get_cursor)
        self.tags = SQLiteTags(self.get_cursor)
        self.task_sets = SQLiteTaskSet(self.get_cursor)
        self.token_sets = SQLiteTokenSet(self.get_cursor)
        self.url_sets = SQLiteURLSet(self.get_cursor)

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
        Automatically applies new migrations when the application starts.
        """
        log_info('SQLITE', 'Checking for database migrations...')

        migration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migration')
        
        # 1. Get current version from DB
        current_version = 0
        try:
            with self.get_cursor() as cursor:
                # Check if config table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
                if cursor.fetchone():
                    cursor.execute("SELECT value FROM config WHERE key='schema-version'")
                    row = cursor.fetchone()
                    if row:
                        current_version = int(row[0])
        except Exception as e:
            log_info("SQLITE", f"Could not determine schema version (assuming 0): {e}")

        # 2. Find migration scripts
        migration_files = []
        if os.path.exists(migration_dir):
            for f in os.listdir(migration_dir):
                if f.endswith('.sql'):
                    parts = f.split('_', 1)
                    if len(parts) > 1 and parts[0].isdigit():
                        version = int(parts[0])
                        if version > current_version:
                            migration_files.append((version, f))
        
        migration_files.sort()

        if not migration_files:
            log_info("SQLITE", "Database is up to date.")
            return

        for version, filename in migration_files:
            log_info("SQLITE", f"Applying migration {filename}...")
            script_path = os.path.join(migration_dir, filename)
            
            try:
                with open(script_path, 'r') as f:
                    sql_script = f.read()

                with self.start_transaction() as session:
                    with self.get_cursor(session=session) as cursor:
                        cursor.executescript(sql_script)
                
                log_info("SQLITE", f"Migration {filename} applied successfully.")
            except Exception as e:
                log_error("SQLITE", f"Error applying migration {filename}: {str(e)}")
                raise e

        log_info("SQLITE", "All migrations applied successfully.")

    @contextmanager
    def start_transaction(self) -> Generator[MyTransactionType, None, None]:
        # for a sqlite transaction it's only required to reuse the same connection
        # commit / rollback is automatically handled when the with block is exited
        with self.get_connection(session=None) as conn:
            yield conn
