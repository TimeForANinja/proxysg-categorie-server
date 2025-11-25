from typing import List

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.dbmodel.staging import ActionType, ActionTable
from db.middleware.abc.sub_category_db import MiddlewareDBSubCategory
from db.middleware.stagingdb.cache import StagedCollection
from db.middleware.stagingdb.category_db import StagingDBCategory
from db.middleware.stagingdb.utils.overloading import add_staged_change


class StagingDBSubCategory(MiddlewareDBSubCategory):
    def __init__(self, db: DBInterface, staged: StagedCollection, categories: StagingDBCategory):
        self._db = db
        self._staged = staged
        self._category_db = categories

    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        return self._category_db.get_category(category_id).nested_categories

    def add_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str):
        # Get current sub-categories
        current_sub_cats = self.get_sub_categories_by_id(cat_id)

        # Add the new sub-category if it's not already there
        if sub_cat_id not in current_sub_cats:
            new_sub_cats = current_sub_cats + [sub_cat_id]

            # Use stage_update to create and add the staged change
            add_staged_change(
                action_type=ActionType.SET_CATS,
                action_table=ActionTable.CATEGORY,
                auth=auth,
                obj_id=cat_id,
                update_data={
                    'nested_categories': new_sub_cats
                },
                staged=self._staged,
            )

    def delete_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str):
        # Get current sub-categories
        current_sub_cats = self.get_sub_categories_by_id(cat_id)

        # Remove the sub-category if it exists
        if sub_cat_id in current_sub_cats:
            new_sub_cats = [c for c in current_sub_cats if c != sub_cat_id]

            # Use stage_update to create and add the staged change
            add_staged_change(
                action_type=ActionType.SET_CATS,
                action_table=ActionTable.CATEGORY,
                auth=auth,
                obj_id=cat_id,
                update_data={
                    'nested_categories': new_sub_cats
                },
                staged=self._staged,
            )

    def set_sub_categories(self, auth: AuthUser, cat_id: str, cat_ids: List[str]):
        # Use stage_update to create and add the staged change
        add_staged_change(
            action_type=ActionType.SET_CATS,
            action_table=ActionTable.CATEGORY,
            auth=auth,
            obj_id=cat_id,
            update_data={
                'nested_categories': cat_ids
            },
            staged=self._staged,
        )
