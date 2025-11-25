import orjson
from pymongo import UpdateOne
from pymongo.database import Database

from db.backend.abc.util.types import MyTransactionType
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs


def apply(db: Database, session: MyTransactionType) -> None:
    """
    Migration 2:
    1) Backfill urls.bc_last_set = 0 where missing or null
    2) Convert task.user from string to AuthUser JSON
    3) update the schema version to 2
    """
    # 1) Backfill urls.bc_last_set = 0 where missing or null
    url_filter = {
        "$or": [
            {"bc_last_set": {"$exists": False}},
            {"bc_last_set": None},
        ]
    }
    db["urls"].update_many(
        url_filter,
        {"$set": {"bc_last_set": 0}},
        **mongo_transaction_kwargs(session),
    )

    # 2) Convert task.user from string to AuthUser JSON
    cursor = db["tasks"].find(
        {"user": {"$type": "string"}},
        projection={"_id": 1, "user": 1},
        **mongo_transaction_kwargs(session),
    )
    updates = []
    for doc in cursor:
        username = doc.get("user")
        payload = {"username": username, "roles": []}
        updates.append(UpdateOne(
            {"_id": doc["_id"]},
            {"$set": {"user": orjson.dumps(payload).decode("utf-8")}})
        )
    if updates:
        db["tasks"].bulk_write(updates, **mongo_transaction_kwargs(session))

    # 3) Update Schema Version
    db['config'].update_one(
        {'key': 'schema-version'},
        {'$set': {'value': 2}},
        upsert=True,
        **mongo_transaction_kwargs(session),
    )
