import sqlite3
from contextlib import AbstractContextManager
from typing import Protocol, Optional

from db.backend.abc.util.types import MyTransactionType


class GetCursorProtocol(Protocol):
    """Protocol for get_cursor callable that accepts optional session parameter."""
    def __call__(self, session: Optional[MyTransactionType] = None) -> AbstractContextManager[sqlite3.Cursor]:
        ...
