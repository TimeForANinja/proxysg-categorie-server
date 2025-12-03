import os
import importlib.util
from typing import Generator, List, Tuple
from pymongo import MongoClient
from contextlib import contextmanager
from pymongo.synchronous.client_session import ClientSession

from auth.auth_user import AUTH_USER_SYSTEM
from log import log_debug, log_info, log_error
from db.backend.abc.db import DBInterface
from db.backend.mongodb.category_db import MongoDBCategory
from db.backend.mongodb.history_db import MongoDBHistory
from db.backend.mongodb.staging_db import MongoDBStaging
from db.backend.mongodb.sub_category_db import MongoDBSubCategory
from db.backend.mongodb.task_db import MongoDBTask
from db.backend.mongodb.token_category_db import MongoDBTokenCategory
from db.backend.mongodb.token_db import MongoDBToken
from db.backend.mongodb.url_db import MongoDBURL
from db.backend.mongodb.url_category_db import MongoDBURLCategory
from db.backend.mongodb.config_db import MongoDBConfig, CONFIG_VAR_SCHEMA_VERSION


class MyMongoDB(DBInterface):
    history: MongoDBHistory

    def __init__(
        self,
        client: MongoClient,
        database_name: str,
        disable_transaction: bool = False,
    ):
        super().__init__()

        self.client = client
        self.db = self.client[database_name]
        self.disable_transaction = disable_transaction

        # Initialize the config collection first to manage a schema version
        self.config = MongoDBConfig(self.db)

        self.categories = MongoDBCategory(self.db)
        self.sub_categories = MongoDBSubCategory(self.db)
        self.history = MongoDBHistory(self.db)
        self.tokens = MongoDBToken(self.db)
        self.token_categories = MongoDBTokenCategory(self.db)
        self.urls = MongoDBURL(self.db)
        self.url_categories = MongoDBURLCategory(self.db)
        self.tasks = MongoDBTask(self.db)
        self.staging = MongoDBStaging(self.db)

    def close(self):
        log_debug("MONGODB", "Closing Client")
        self.client.close()

    def migrate(self):
        """
        Run Initialization and Optimization steps.
        This can include anything from pushing initial data to creating indexes.
        Also run MongoDB migration scripts.
        """
        # check if we're using a new MongoDB
        if not self.history.has_history_events():
            log_info("MONGODB", "Initializing database")
            # create initial commit
            self.history.add_history_event('Initial setup', AUTH_USER_SYSTEM, [], [], [])
            # Create index on token field
            self.db['tokens'].create_index({'token': 1}, unique=True, name='token_token_idx')

        # Run db migrations
        self._migrate_db_schema()

    def _migrate_db_schema(self) -> None:
        # Get current schema version
        current_version = self.config.get_schema_version()
        log_info('MONGODB', f'Current schema version: {current_version}')

        # Find migration scripts (python files) in the migration directory
        migration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migration')
        os.makedirs(migration_dir, exist_ok=True)

        migration_files: List[Tuple[int, str]] = []
        try:
            for file in os.listdir(migration_dir):
                if file.endswith('.py') and file[0].isdigit():
                    try:
                        version = int(file.split('_')[0])
                        migration_files.append((version, os.path.join(migration_dir, file)))
                    except (ValueError, IndexError):
                        log_error('MONGODB', f'Skipping invalid migration file: {file}')
                        continue
        except FileNotFoundError:
            # no migrations yet
            return

        # Sort migration files by version (ascending)
        migration_files.sort(key=lambda x: x[0])

        for version, file_path in migration_files:
            if version <= current_version:
                log_debug('MONGODB', f"Skipping migration: {os.path.basename(file_path)} (version {version} is older or equal to current version {current_version})")
                continue

            log_debug('MONGODB', f'Applying migration: {os.path.basename(file_path)}')
            try:
                # Dynamically import the migration module
                spec = importlib.util.spec_from_file_location(f'mongo_migration_{version}', file_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f'Cannot load migration file: {file_path}')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Each migration module must expose an `apply(db, session)` function (no-op if nothing to change)
                apply_fn = getattr(module, 'apply', None)
                if apply_fn is None:
                    raise AttributeError(f'Migration file {file_path} does not define an apply(db, session) function')

                # Run migration inside a transaction
                with self.start_transaction() as session:
                    apply_fn(self.db, session)
                    # Update the schema version as part of the same transaction
                    self.config.set_int(CONFIG_VAR_SCHEMA_VERSION, version, session=session)
                    # leave the with block to commit the transaction

                log_info('MONGODB', f'Applied migration: {os.path.basename(file_path)}')
                current_version = version
            except Exception as e:
                log_error('MONGODB', f'Error applying migration {os.path.basename(file_path)}: {str(e)}')
                # migration failed
                # raise to stop the server since the DB is not as expected
                raise

    @contextmanager
    def start_transaction(self) -> Generator[ClientSession, None, None]:
        # start a new session, and a transaction in that session
        with self.client.start_session() as session:
            if self.disable_transaction:
                # not all MongoDB-Installations support transactions,
                # so add a feature flag to disable transactions
                yield session

            with session.start_transaction():
                # yield the session to the caller, so they can use it in their transaction
                # when the caller is done it will automatically close both the transaction and the session
                yield session
