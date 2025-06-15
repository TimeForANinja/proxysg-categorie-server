from typing import List, Optional

from auth.auth_user import AuthUser
from db.stagingdb.category_db import StagingDBCategory
from db.stagingdb.url_category_db import StagingDBURLCategory
from db.stagingdb.url_db import StagingDBURL
from db.util.parse_existing_db import create_in_db, create_urls_db, ExistingCat


class StagingDBExisting:
    def __init__(
            self,
            db_url: StagingDBURL,
            db_cats: StagingDBCategory,
            db_url_cats: StagingDBURLCategory
    ):
        self._db_url = db_url
        self._db_cats = db_cats
        self._db_url_cats = db_url_cats

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
        create_in_db(self._db_url, self._db_cats, self._db_url_cats, auth, categories, prefix)

        if uncategorized is not None:
            create_urls_db(self._db_url, auth, uncategorized)
