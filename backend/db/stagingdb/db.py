from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.staging import ActionTable
from db.stagingdb.category_db import StagingDBCategory
from db.stagingdb.existing import StagingDBExisting
from db.stagingdb.history_db import StagingDBHistory
from db.stagingdb.sub_category_db import StagingDBSubCategory
from db.stagingdb.task_db import StagingDBTask
from db.stagingdb.token_category_db import StagingDBTokenCategory
from db.stagingdb.token_db import StagingDBToken
from db.stagingdb.url_category_db import StagingDBURLCategory
from db.stagingdb.url_db import StagingDBURL
from db.stagingdb.cache import StagedCollection


class StagingDB:
    categories: StagingDBCategory
    sub_categories: StagingDBSubCategory
    history: StagingDBHistory
    tokens: StagingDBToken
    token_categories: StagingDBTokenCategory
    urls: StagingDBURL
    url_categories: StagingDBURLCategory
    existing: StagingDBExisting
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
        self.history = StagingDBHistory(self._main_db)
        self.tokens = StagingDBToken(self._main_db, self._staged)
        self.token_categories = StagingDBTokenCategory(self._main_db, self._staged, self.tokens)
        self.urls = StagingDBURL(self._main_db, self._staged)
        self.url_categories = StagingDBURLCategory(self._main_db, self._staged, self.urls)
        self.existing = StagingDBExisting(self.urls, self.categories, self.url_categories)
        self.tasks = StagingDBTask(self._main_db, self._staged)

    def close(self):
        self._main_db.close()

    def commit(self, user: AuthUser):
        """
        Push all staged changes to the main database.

        :param user: User object for the user who is committing the changes
        """
        # Collect atomics from for all changes
        atomics = []
        ref_token = []
        ref_url = []
        ref_category = []

        # apply changes to the database
        for change in self._staged.iter():
            atomic = None
            if change.action_table == ActionTable.TOKEN:
                atomic = self.tokens.commit(change)
            elif change.action_table == ActionTable.URL:
                atomic = self.urls.commit(change)
            elif change.action_table == ActionTable.CATEGORY:
                atomic = self.categories.commit(change)

            # if a change was done, store the atomic
            if atomic:
                atomics.append(atomic)
                # also store the refs to skip one loop
                ref_token += atomic.ref_token
                ref_url += atomic.ref_url
                ref_category += atomic.ref_category

        # Create a single history event with all atomics
        if atomics:
            self._main_db.history.add_history_event(
                action="Commit",
                user=user,
                # use list(set(xxx)) to remove duplicates
                ref_token=list(set(ref_token)),
                ref_url=list(set(ref_url)),
                ref_category=list(set(ref_category)),
                atomics=atomics,
            )

        # remove all staged events, now that they are committed
        self._staged.clear()
