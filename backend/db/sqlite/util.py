import sqlite3
from typing import List

def _fetch_table_list(conn: sqlite3.Connection) -> List[str]:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    # Extract the table names from the tuples returned by fetchall
    return [
        table[0] for table in tables
    ]

def split_opt_int_group(group: str | None) -> List[int]:
    if group is None:
        return []
    return split_int_group(group)

def split_int_group(group: str) -> List[int]:
    parts = group.split(",")
    return [
        int(part)
        for part
        in parts
    ]
