import time
from typing import List

from auth.auth_user import AUTH_USER_SYSTEM
from db.backend.abc.db import DBInterface
from db.dbmodel.history import History, Atomic


class StagingDBHistory:
    def __init__(self, db: DBInterface):
        self._db = db

    def get_history_events(self) -> List[History]:
        history = self._db.history.get_history_events()
        pending = self._db.staging.get_staged_changes()
        history.append(History(
            id="-1",
            time=int(time.time()),
            user=AUTH_USER_SYSTEM,
            description="Pending changes",
            ref_token=[],
            ref_url=[],
            ref_category=[],
            atomics=[Atomic(
                id=p.uid,
                user=p.auth,
                action=p.action_type.value,
                timestamp=p.timestamp,
                ref_token=[],
                ref_url=[],
                ref_category=[],
                description=p.action_type.value + " on " + p.action_table.value,
            ) for p in pending],
        ))
        return history
