import time
from typing import List, Callable, Tuple

from auth.auth_user import AUTH_USER_SYSTEM
from db.backend.abc.db import DBInterface
from db.dbmodel.history import History, Atomic
from db.middleware.abc.history_db import MiddlewareDBHistory


class StagingDBHistory(MiddlewareDBHistory):
    def __init__(
        self,
        db: DBInterface,
        get_pending: Callable[[], Tuple[List[Atomic], List[str], List[str], List[str]]],
    ):
        self._db = db
        self._get_pending = get_pending

    def get_history_events(self) -> List[History]:
        history = self._db.history.get_history_events()

        # if we have pending changes, add a fake event for them
        atomics, ref_token, ref_url, ref_category = self._get_pending()
        if atomics:
            history.append(History(
                id="-1",
                time=int(time.time()),
                user=AUTH_USER_SYSTEM,
                description="Pending changes",
                ref_token=ref_token,
                ref_url=ref_url,
                ref_category=ref_category,
                atomics=atomics,
            ))

        return history
