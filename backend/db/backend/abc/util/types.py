import sqlite3
from typing import Union

from pymongo.synchronous.client_session import ClientSession

# custom union type for transactions
MyTransactionType = Union[ClientSession, sqlite3.Connection]
