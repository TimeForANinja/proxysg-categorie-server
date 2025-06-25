from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.staging import ActionType, ActionTable
from db.stagingdb.cache import StagedCollection
from db.stagingdb.url_db import StagingDBURL
from db.stagingdb.utils.overloading import add_staged_change


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

            # Use stage_update to create and add the staged change
            add_staged_change(
                action_type=ActionType.SET_CATS,
                action_table=ActionTable.URL,
                auth=auth,
                obj_id=url_id,
                update_data={
                    'categories': new_categories
                },
                staged=self._staged,
            )

    def delete_url_category(self, auth: AuthUser, url_id: str, cat_id: str) -> None:
        # Get current categories
        current_categories = self.get_url_categories_by_url(url_id)

        # Remove the category if it exists
        if cat_id in current_categories:
            new_categories = [c for c in current_categories if c != cat_id]

            # Use stage_update to create and add the staged change
            add_staged_change(
                action_type=ActionType.SET_CATS,
                action_table=ActionTable.URL,
                auth=auth,
                obj_id=url_id,
                update_data={
                    'categories': new_categories
                },
                staged=self._staged,
            )

    def set_url_categories(self, auth: AuthUser, url_id: str, cat_ids: List[str]) -> None:
        # Use stage_update to create and add the staged change
        add_staged_change(
            action_type=ActionType.SET_CATS,
            action_table=ActionTable.URL,
            auth=auth,
            obj_id=url_id,
            update_data={
                'categories': cat_ids
            },
            staged=self._staged,
        )
