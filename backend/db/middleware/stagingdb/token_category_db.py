from typing import List

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.dbmodel.staging import ActionType, ActionTable
from db.middleware.abc.token_category_db import MiddlewareDBTokenCategory
from db.middleware.stagingdb.cache import StagedCollection
from db.middleware.stagingdb.token_db import StagingDBToken
from db.middleware.stagingdb.utils.overloading import add_staged_change


class StagingDBTokenCategory(MiddlewareDBTokenCategory):
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

            # Use stage_update to create and add the staged change
            add_staged_change(
                action_type=ActionType.SET_CATS,
                action_table=ActionTable.TOKEN,
                auth=auth,
                obj_id=token_id,
                update_data={
                    'categories': new_categories
                },
                staged=self._staged,
            )

    def delete_token_category(self, auth: AuthUser, token_id: str, cat_id: str) -> None:
        # Get current categories
        current_categories = self.get_token_categories_by_token(token_id)

        # Remove the category if it exists
        if cat_id in current_categories:
            new_categories = [c for c in current_categories if c != cat_id]

            # Use stage_update to create and add the staged change
            add_staged_change(
                action_type=ActionType.SET_CATS,
                action_table=ActionTable.TOKEN,
                auth=auth,
                obj_id=token_id,
                update_data={
                    'categories': new_categories
                },
                staged=self._staged,
            )

    def set_token_categories(self, auth: AuthUser, token_id: str, cat_ids: List[str]) -> None:
        # Use stage_update to create and add the staged change
        add_staged_change(
            action_type=ActionType.SET_CATS,
            action_table=ActionTable.TOKEN,
            auth=auth,
            obj_id=token_id,
            update_data={
                'categories': cat_ids
            },
            staged=self._staged,
        )
