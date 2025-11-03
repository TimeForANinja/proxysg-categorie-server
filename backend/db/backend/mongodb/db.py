from typing import Generator
from pymongo import MongoClient
from contextlib import contextmanager
from pymongo.synchronous.client_session import ClientSession

from log import log_debug
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


class MyMongoDB(DBInterface):
    def __init__(
            self,
            client: MongoClient,
            database_name: str,
    ):
        super().__init__()

        self.client = client
        self.db = self.client[database_name]

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

    @contextmanager
    def start_transaction(self) -> Generator[ClientSession, None, None]:
        # start a new session, and a transaction in that session
        with self.client.start_session() as session:
            with session.start_transaction():
                # yield the session to the caller, so they can use it in their transaction
                # when the caller is done it will automatically close both the transaction and the session
                yield session
