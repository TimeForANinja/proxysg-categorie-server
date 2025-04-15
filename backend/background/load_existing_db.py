import time
from pathlib import Path

from db.db_singleton import get_db
from log import log_info
from routes.load_existing import parse_db, create_in_db


def load_existing_file(filepath="./data/local_db.txt", prefix_cats=""):
    """
    Load an existing Local DB and add it to our DB

    :param filepath: The path to the existing Local DB file
    :param prefix_cats: A prefix to add to all categories in the DB
    :prefix_cats: A prefix to add to all categories in the DB
    """

    # check if we have a local db file
    existing_local_db = Path(filepath)
    if not existing_local_db.is_file():
        log_info(
            "background",
            "Existing LocalDB not found",
            {"filepath": filepath}
        )
        return

    # load the content, parse it
    # and push the parsed URLs and Cats to the DB
    file_str = existing_local_db.read_text(encoding="utf-8")
    db_if = get_db()
    new_cats = parse_db(file_str)

    # add prefix to all cats
    for cat in new_cats:
        cat.name = prefix_cats + cat.name

    create_in_db(db_if, new_cats)

    log_info(
        "background",
        f"Loaded {len(new_cats)} Cats from existing LocalDB",
        {"filepath": filepath}
    )
