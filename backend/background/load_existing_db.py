import time
from pathlib import Path

from db.db_singleton import get_db
from routes.load_existing import parse_db, create_in_db


def load_existing_file(filepath="./data/local_db.txt"):
    # check if we have a local db file
    existing_local_db = Path(filepath)
    if not existing_local_db.is_file():
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Skipped loading existing LocalDB - File not found")
        return

    # load the content, parse it
    # and push the parsed URLs and Cats to the DB
    file_str = existing_local_db.read_text(encoding="utf-8")
    db_if = get_db()
    new_cats = parse_db(file_str)
    create_in_db(db_if, new_cats)

    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Finished loading existing LocalDB")
