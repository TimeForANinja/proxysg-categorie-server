from typing import List, Tuple

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.dbmodel.history import Atomic
from db.dbmodel.staging import ActionTable
from db.middleware.abc.db import MiddlewareDB
from db.middleware.stagingdb.cache import StagedCollection
from db.middleware.stagingdb.category_db import StagingDBCategory
from db.middleware.stagingdb.history_db import StagingDBHistory
from db.middleware.stagingdb.sub_category_db import StagingDBSubCategory
from db.middleware.stagingdb.task_db import StagingDBTask
from db.middleware.stagingdb.token_category_db import StagingDBTokenCategory
from db.middleware.stagingdb.token_db import StagingDBToken
from db.middleware.stagingdb.url_category_db import StagingDBURLCategory
from db.middleware.stagingdb.url_db import StagingDBURL


class StagingDB(MiddlewareDB):
    categories: StagingDBCategory
    sub_categories: StagingDBSubCategory
    history: StagingDBHistory
    tokens: StagingDBToken
    token_categories: StagingDBTokenCategory
    urls: StagingDBURL
    url_categories: StagingDBURLCategory
    tasks: StagingDBTask

    def __init__(
            self,
            main_db: DBInterface,
    ):
        super().__init__()
        self._main_db = main_db
        self._staged = StagedCollection(self._main_db)

        self.categories = StagingDBCategory(self._main_db, self._staged)
        self.sub_categories = StagingDBSubCategory(self._main_db, self._staged, self.categories)
        self.history = StagingDBHistory(
            self._main_db,
            lambda: self._commit_modules(False)
        )
        self.tokens = StagingDBToken(self._main_db, self._staged)
        self.token_categories = StagingDBTokenCategory(self._main_db, self._staged, self.tokens)
        self.urls = StagingDBURL(self._main_db, self._staged)
        self.url_categories = StagingDBURLCategory(self._main_db, self._staged, self.urls)
        self.tasks = StagingDBTask(self._main_db, self._staged)

    def close(self):
        self._main_db.close()

    def _commit_modules(self, dry_run: bool) -> Tuple[
        List[Atomic],
        List[str],
        List[str],
        List[str],
    ]:
        # Collect atomics from for all changes
        atomics: List[Atomic] = []
        ref_token: List[str] = []
        ref_url: List[str] = []
        ref_category: List[str] = []

        # apply changes to the database
        for change in self._staged.iter():
            atomic = None
            if change.action_table == ActionTable.TOKEN:
                atomic = self.tokens.commit(change, dry_run)
            elif change.action_table == ActionTable.URL:
                atomic = self.urls.commit(change, dry_run)
            elif change.action_table == ActionTable.CATEGORY:
                atomic = self.categories.commit(change, dry_run)

            # if a change was done, store the atomic
            if atomic:
                atomics.append(atomic)
                # also store the refs to skip one loop
                ref_token += atomic.ref_token
                ref_url += atomic.ref_url
                ref_category += atomic.ref_category


        # use list(set(xxx)) to remove duplicates
        ref_token = list(set(ref_token))
        ref_url = list(set(ref_url))
        ref_category = list(set(ref_category))

        return atomics, ref_token, ref_url, ref_category

    def commit(self, user: AuthUser):
        """
        Push all staged changes to the main database.

        :param user: User object for the user who is committing the changes
        """
        atomics, ref_token, ref_url, ref_category = self._commit_modules(False)

        # Create a single history event with all atomics
        if atomics:
            self._main_db.history.add_history_event(
                action="Commit",
                user=user,
                ref_token=ref_token,
                ref_url=ref_url,
                ref_category=ref_category,
                atomics=atomics,
            )

        # remove all staged events, now that they are committed
        self._staged.clear()
