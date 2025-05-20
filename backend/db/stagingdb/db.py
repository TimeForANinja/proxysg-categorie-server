from db.abc.db import DBInterface
from db.stagingdb.category_db import StagingDBCategory
from db.stagingdb.existing import StagingDBExisting
from db.stagingdb.history_db import StagingDBHistory
from db.stagingdb.sub_category_db import StagingDBSubCategory
from db.stagingdb.token_category_db import StagingDBTokenCategory
from db.stagingdb.token_db import StagingDBToken
from db.stagingdb.url_category_db import StagingDBURLCategory
from db.stagingdb.url_db import StagingDBURL
from db.stagingdb.cache import StagedCollection, StagedChangeTable


class StagingDB:
    categories: StagingDBCategory
    sub_categories: StagingDBSubCategory
    history: StagingDBHistory
    tokens: StagingDBToken
    token_categories: StagingDBTokenCategory
    urls: StagingDBURL
    url_categories: StagingDBURLCategory
    existing: StagingDBExisting

    def __init__(
            self,
            main_db: DBInterface,
    ):
        super().__init__()

        self._main_db = main_db
        self._staged: StagedCollection = StagedCollection()

        self.categories = StagingDBCategory(self._main_db, self._staged)
        self.sub_categories = StagingDBSubCategory(self._main_db, self._staged, self.categories)
        self.history = StagingDBHistory(self._main_db)
        self.tokens = StagingDBToken(self._main_db, self._staged)
        self.token_categories = StagingDBTokenCategory(self._main_db, self._staged, self.tokens)
        self.urls = StagingDBURL(self._main_db, self._staged)
        self.url_categories = StagingDBURLCategory(self._main_db, self._staged, self.urls)
        self.existing = StagingDBExisting(self._main_db)

    def close(self):
        self._main_db.close()

    def commit(self):
        """
        Push all staged changes to the main database.
        """
        for change in self._staged.iter():
            if change.table == StagedChangeTable.TOKEN:
                self.tokens.commit(change)
            elif change.table == StagedChangeTable.URL:
                self.urls.commit(change)
            elif change.table == StagedChangeTable.CATEGORY:
                self.categories.commit(change)

        self._staged.clear()
