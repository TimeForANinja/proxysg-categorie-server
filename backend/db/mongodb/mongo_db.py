from pymongo import MongoClient

from db.db import DBInterface
from db.mongodb.category_db import MongoDBCategory
from db.mongodb.history_db import MongoDBHistory
from db.mongodb.sub_category_db import MongoDBSubCategory
from db.mongodb.task_db import MongoDBTask
from db.mongodb.token_category_db import MongoDBTokenCategory
from db.mongodb.token_db import MongoDBToken
from db.mongodb.url_db import MongoDBURL
from db.mongodb.url_category_db import MongoDBURLCategory


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

    def close(self):
        # no call to self.client.close() required after each context closure
        # since the DB is external, we do not need to worry about thread safety here
        pass
