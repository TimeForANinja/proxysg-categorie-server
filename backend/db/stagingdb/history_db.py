from typing import List

from db.abc.db import DBInterface
from db.abc.history import History


class StagingDBHistory:
    def __init__(self, db: DBInterface):
        self._db = db

    def get_history_events(self) -> List[History]:
        return self._db.history.get_history_events()
