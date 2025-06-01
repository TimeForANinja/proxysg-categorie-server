import time
from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.staging import ActionType, ActionTable
from db.stagingdb.cache import StagedChange, StagedCollection
from db.stagingdb.token_db import StagingDBToken


class StagingDBTokenCategory:
    def __init__(self, db: DBInterface, staged: StagedCollection, tokens: StagingDBToken):
        self._db = db
        self._staged = staged
        self._token_db = tokens

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        return self._token_db.get_token(token_id).categories

    def add_token_category(self, auth: AuthUser, token_id: str, cat_id: str) -> None:
        # Get current categories
        current_categories = self.get_token_categories_by_token(token_id)

        # Add the new category if it's not already there
        if cat_id not in current_categories:
            new_categories = current_categories + [cat_id]

            # Create a staged change for the TOKEN table
            staged_change = StagedChange(
                action_type=ActionType.UPDATE,
                action_table=ActionTable.TOKEN,
                auth=auth,
                uid=token_id,
                data={
                    'categories': new_categories
                },
                timestamp=int(time.time()),
            )
            # Add the staged change to the staging DB
            self._staged.add(staged_change)

    def delete_token_category(self, auth: AuthUser, token_id: str, cat_id: str) -> None:
        # Get current categories
        current_categories = self.get_token_categories_by_token(token_id)

        # Remove the category if it exists
        if cat_id in current_categories:
            new_categories = [c for c in current_categories if c != cat_id]

            # Create a staged change for the TOKEN table
            staged_change = StagedChange(
                action_type=ActionType.UPDATE,
                action_table=ActionTable.TOKEN,
                auth=auth,
                uid=token_id,
                data={
                    'categories': new_categories
                },
                timestamp=int(time.time()),
            )
            # Add the staged change to the staging DB
            self._staged.add(staged_change)

    def set_token_categories(self, auth: AuthUser, token_id: str, cat_ids: List[str]) -> None:
        # Create a staged change for the TOKEN table with the new categories
        staged_change = StagedChange(
            action_type=ActionType.UPDATE,
            action_table=ActionTable.TOKEN,
            auth=auth,
            uid=token_id,
            data={
                'categories': cat_ids
            },
            timestamp=int(time.time()),
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)
