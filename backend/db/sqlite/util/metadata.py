import sqlite3
from typing import List


def fetch_table_list(conn: sqlite3.Connection) -> List[str]:
    """
    This utility function returns a list of table names in the SQLite database.

    :param conn: The SQLite connection object
    :return: A list of table names
    """
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\'')
    tables = cursor.fetchall()
    # Extract the table names from the tuples returned by fetchall
    return [
        table[0] for table in tables
    ]
