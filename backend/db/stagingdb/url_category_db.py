from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.stagingdb.cache import StagedChange, StagedChangeAction, StagedCollection, StagedChangeTable
from db.stagingdb.url_db import StagingDBURL


class StagingDBURLCategory:
    def __init__(self, db: DBInterface, staged: StagedCollection, urls: StagingDBURL):
        self._db = db
        self._staged = staged
        self._url_db = urls

    def get_url_categories_by_url(self, url_id: str) -> List[str]:
        return self._url_db.get_url(url_id).categories

    def add_url_category(self, auth: AuthUser, url_id: str, cat_id: str) -> None:
        # Get current categories
        current_categories = self.get_url_categories_by_url(url_id)

        # Add the new category if it's not already there
        if cat_id not in current_categories:
            new_categories = current_categories + [cat_id]

            # Create a staged change for the URL table
            staged_change = StagedChange(
                action_type=StagedChangeAction.UPDATE,
                table=StagedChangeTable.URL,
                auth=auth,
                uid=url_id,
                data={
                    'categories': new_categories
                },
            )
            # Add the staged change to the staging DB
            self._staged.add(staged_change)

    def delete_url_category(self, auth: AuthUser, url_id: str, cat_id: str) -> None:
        # Get current categories
        current_categories = self.get_url_categories_by_url(url_id)

        # Remove the category if it exists
        if cat_id in current_categories:
            new_categories = [c for c in current_categories if c != cat_id]

            # Create a staged change for the URL table
            staged_change = StagedChange(
                action_type=StagedChangeAction.UPDATE,
                table=StagedChangeTable.URL,
                auth=auth,
                uid=url_id,
                data={
                    'categories': new_categories
                },
            )
            # Add the staged change to the staging DB
            self._staged.add(staged_change)

    def set_url_categories(self, auth: AuthUser, url_id: str, cat_ids: List[str]) -> None:
        # Create a staged change for the URL table with the new categories
        staged_change = StagedChange(
            action_type=StagedChangeAction.UPDATE,
            table=StagedChangeTable.URL,
            auth=auth,
            uid=url_id,
            data={
                'categories': cat_ids
            },
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

    def commit(self, change: StagedChange) -> None:
        # This is no longer needed as changes are stored in the URL table
        # and will be committed by the url_db.py commit method
        pass
