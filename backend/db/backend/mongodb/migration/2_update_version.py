import time
import orjson
from pymongo import UpdateOne
from pymongo.database import Database

from auth.auth_user import AuthUser, AUTH_USER_SYSTEM
from db.backend.abc.util.types import MyTransactionType
from db.backend.mongodb.util.typecheck import is_json
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs


def update_user(db: Database, session: MyTransactionType, table: str) -> None:
    """Replace the user field in all a certain table with a JSON variant."""
    cursor = db[table].find(
        {"user": {"$type": "string"}},
        projection={"_id": 1, "user": 1},
        **mongo_transaction_kwargs(session),
    )
    updates = []
    for doc in cursor:
        username = doc.get("user")
        if is_json(username):
            continue
        # if it's not already a JSON, make it one
        payload = orjson.dumps({"username": username, "roles": []}).decode("utf-8")
        updates.append(UpdateOne(
            {"_id": doc["_id"]},
            {"$set": {"user": payload}})
        )
    if updates:
        db[table].bulk_write(updates, **mongo_transaction_kwargs(session))


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
    update_user(db, session, "tasks")

    # 3) Convert history.user from string to AuthUser JSON
    update_user(db, session, "history")

    # 4) Update Schema Version
    db['config'].update_one(
        {'key': 'schema-version'},
        {'$set': {'value': 2}},
        upsert=True,
        **mongo_transaction_kwargs(session),
    )

    # 5) Add History Event
    db['history'].insert_one(
        {
            'time': int(time.time()),
            'description': "Updated schema version to 2",
            'user': AuthUser.serialize(AUTH_USER_SYSTEM),
            'ref_token': [],
            'ref_url': [],
            'ref_category': [],
        },
        **mongo_transaction_kwargs(session),
    )
