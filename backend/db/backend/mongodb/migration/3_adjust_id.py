import time
from bson import ObjectId
from pymongo import UpdateOne, DeleteOne, InsertOne, UpdateMany
from pymongo.database import Database
from pymongo.collection import Collection
from uuid import uuid7

from auth.auth_user import AuthUser, AUTH_USER_SYSTEM
from db.backend.abc.util.types import MyTransactionType
from db.backend.mongodb.util.transactions import mongo_transaction_kwargs


def reinsert_uid(col: Collection, session: MyTransactionType) -> None:
    # pass 1 - build a LUT of uid for all objects with valid _id
    cursor1 = col.find(
        {},
        projection={'_id': 1, 'uid': 1},
        **mongo_transaction_kwargs(session)
    )
    known_valid_uid = {
        doc.get('uid')
        for doc in cursor1
        if isinstance(doc['_id'], ObjectId)
    }

    # pass 2 - go through the collection and queue modifications
    # we need to do a second query, since we
    # a) already exhausted the first cursor and
    # b) since we did a projection initially
    cursor2 = col.find({}, **mongo_transaction_kwargs(session))

    inserts = []
    deletes = []

    for doc in cursor2:
        if isinstance(doc['_id'], ObjectId):
            # we only want to update non-ObjectId documents
            continue

        # insert only if we do no (yet) have a valid one in the DB
        # this is required to catch the edge-case of the script failing mid-way through a first run
        if doc.get('uid') not in known_valid_uid:
            # we unfortunately can't update the _id property in mongodb,
            # so we need create and insert a fixed copy of the document
            new_doc = doc.copy()
            new_doc['_id'] = ObjectId()
            inserts.append(InsertOne(new_doc))

        # always do the delete; not just when we inserted
        # this helps make the script idempotent
        deletes.append(DeleteOne({'_id': doc['_id']}))

    if inserts:
        col.bulk_write(inserts, **mongo_transaction_kwargs(session))
    if deletes:
        col.bulk_write(deletes, **mongo_transaction_kwargs(session))


def regenerate_uid(col: Collection, session: MyTransactionType) -> None:
    cursor = col.find(
        {},
        projection={'_id': 1, 'uid': 1},
        **mongo_transaction_kwargs(session)
    )

    updates = []
    for doc in cursor:
        if doc.get('uid'):
            # if we already have a uid, skip this document
            continue

        uid = str(uuid7())
        updates.append(UpdateOne(
            {'_id': doc['_id']},
            {'$set': {'uid': uid}}
        ))

    if updates:
        col.bulk_write(updates, **mongo_transaction_kwargs(session))


def adjust_atomics(db: Database, session: MyTransactionType) -> None:
    cursor = db['history'].find(
        {},
        projection={'_id': 1, 'uid': 1},
        **mongo_transaction_kwargs(session)
    )

    updates = []
    for doc in cursor:
        updates.append(UpdateMany(
            {'history_id': doc['_id']},
            {'$set': {'history_id': doc['uid']}},
        ))

    if updates:
        db['history_atomics'].bulk_write(updates, **mongo_transaction_kwargs(session))


def apply(db: Database, session: MyTransactionType) -> None:
    """
    Migration 3:
    - Generate new "uid" element for all documents
    - adjust history_atomics to use the new history#uid instead of history#_id
    - fix all elements where "_id" is not of type ObjectId by reinserting them
    - add new indexes for the "uid" fields
    """
    # 1) Regenerate uid for all elements
    for table in ['tokens', 'urls', 'categories', 'tasks', 'history']:
        regenerate_uid(db[table], session)

    # 2) adjust atomics to ref the new history#uid instead of history#_id
    adjust_atomics(db, session)

    # 3) Reinsert all elements where "_id" is not of type ObjectId
    for table in ['tokens', 'urls', 'categories', 'tasks', 'history']:
        reinsert_uid(db[table], session)

    # 4) Update Schema Version
    db['config'].update_one(
        {'key': 'schema-version'},
        {'$set': {'value': 3}},
        upsert=True,
        **mongo_transaction_kwargs(session),
    )

    # 5) Add History Event
    db['history'].insert_one(
        {
            'uid': str(uuid7()),
            'time': int(time.time()),
            'description': 'Updated schema version to 3',
            'user': AuthUser.serialize(AUTH_USER_SYSTEM),
            'ref_token': [],
            'ref_url': [],
            'ref_category': [],
        },
        **mongo_transaction_kwargs(session),
    )
