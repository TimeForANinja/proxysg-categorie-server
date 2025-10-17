import sqlite3
from pymongo.synchronous.client_session import ClientSession

# custom union type for transactions
MyTransactionType = ClientSession | sqlite3.Connection
