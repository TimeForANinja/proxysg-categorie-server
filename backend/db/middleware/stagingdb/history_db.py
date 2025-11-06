import time
from typing import List, Callable, Tuple, Optional

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

    def get_history_events(self, include_atomics: bool = False) -> List[History]:
        history = self._db.history.get_history_events(include_atomics=include_atomics)

        # if we have pending changes, add a fake event for them
        if self._db.staging.has_staged_changes():
            dummy_change = History(
                id="-1",
                time=int(time.time()),
                user=AUTH_USER_SYSTEM,
                description="Pending changes",
                ref_token=[],
                ref_url=[],
                ref_category=[],
                atomics=[],
            )
            # only parse staged changes if actually required
            if include_atomics:
                atomics, ref_token, ref_url, ref_category = self._get_pending()
                dummy_change.atomics = atomics
                dummy_change.ref_token = ref_token
                dummy_change.ref_url = ref_url
                dummy_change.ref_category = ref_category

            history.append(dummy_change)
        return history

    def get_history_atomics(
            self,
            references_history: Optional[List[str]] = None,
            references_url: Optional[List[str]] = None,
            references_token: Optional[List[str]] = None,
            references_category: Optional[List[str]] = None,
    ) -> List[Atomic]:
        persistent_atomics = self._db.history.get_history_atomics(
            # filter out the "-1" dummy event
            references_history=[x for x in references_history if x != '-1'],
            references_url=references_url,
            references_token=references_token,
            references_category=references_category,
        )

        # check if we need to fetch staged changes
        # either if the dummy-history was selected
        # or if we filter by url, token or category
        if "-1" in references_history:
            atomics, _, _, _ = self._get_pending()
            persistent_atomics.extend(atomics)
        elif references_url or references_token or references_category:
            atomics, _, _, _ = self._get_pending()
            filtered_atomics = [
                a for a in atomics
                if
                a.ref_url in references_url or a.ref_token in references_token or a.ref_category in references_category
            ]
            persistent_atomics.extend(filtered_atomics)

        return persistent_atomics
