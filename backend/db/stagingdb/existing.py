from typing import List, Optional

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.util.parse_existing_db import create_in_db, create_urls_db, ExistingCat


class StagingDBExisting:
    def __init__(self, db: DBInterface):
        self._db = db

    def save_existing(
            self,
            auth: AuthUser,
            categories: List[ExistingCat],
            prefix: str,
            uncategorized: Optional[List[str]] = None,
    ) -> None:
        """
        Save the parsed existing DB to the current DB.

        :param auth: AuthUser object for the user who is importing the DB
        :param categories: List of categories to import
        :param prefix: Prefix to use for the categories
        :param uncategorized: List of URLs to import as uncategorized (or Null)
        """
        # push the intermediate objects to the main db
        create_in_db(self._db, categories, prefix)
        if uncategorized is not None:
            create_urls_db(self._db, uncategorized)

        # TODO: fill in ref's
        self._db.history.add_history_event('existing db imported', auth, [], [], [])
