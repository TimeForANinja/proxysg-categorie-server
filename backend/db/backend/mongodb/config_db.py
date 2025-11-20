from typing import Optional

from pymongo.database import Database

from db.backend.abc.util.types import MyTransactionType
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs

CONFIG_VAR_SCHEMA_VERSION = 'schema-version'


class MongoDBConfig:
    def __init__(self, db: Database):
        self._db = db
        self._collection = self._db['config']

    def read_int(self, key: str) -> int:
        """Get the value of a config variable, or -1 if it doesn't exist."""
        doc = self._collection.find_one({'key': key}, projection={'_id': 0, 'value': 1})
        if doc is None:
            return -1
        try:
            return int(doc.get('value', -1))
        except (ValueError, TypeError):
            return -1

    def set_int(self, key: str, value: int, session: Optional[MyTransactionType] = None) -> None:
        """
        Set a config variable. If it doesn't exist, create it.

        :param key: The key of the config variable.
        :param value: The value to set.
        :param session: Optional Mongo session to use.
        """
        self._collection.update_one(
            {'key': key},
            {'$set': {'value': int(value)}},
            upsert=True, # create if missing
            **mongo_transaction_kwargs(session),
        )

    def get_schema_version(self) -> int:
        """
        Get the current schema version from the config collection.
        Since this collection does not yet exist for MongoDB in this project,
        default to version 1 when missing, as requested.
        """
        try:
            val = self.read_int(CONFIG_VAR_SCHEMA_VERSION)
        except Exception as e:
            print(e)
            # Any unexpected error: be conservative and treat as missing
            return 1
        # if not set/missing, default to 1 for initial rollout
        return max(val, 1)
