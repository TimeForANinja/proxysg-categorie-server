from typing import List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.stagingdb.cache import StagedChange, StagedChangeAction, StagedCollection, StagedChangeTable
from db.stagingdb.category_db import StagingDBCategory


class StagingDBSubCategory:
    def __init__(self, db: DBInterface, staged: StagedCollection, categories: StagingDBCategory):
        self._db = db
        self._staged = staged
        self._category_db = categories

    def get_sub_categories_by_id(self, category_id: str) -> List[str]:
        return self._category_db.get_category(category_id).nested_categories

    def add_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str) -> None:
        # Get current sub-categories
        current_sub_cats = self.get_sub_categories_by_id(cat_id)

        # Add the new sub-category if it's not already there
        if sub_cat_id not in current_sub_cats:
            new_sub_cats = current_sub_cats + [sub_cat_id]

            # Create a staged change for the CATEGORY table
            staged_change = StagedChange(
                type=StagedChangeAction.UPDATE,
                table=StagedChangeTable.CATEGORY,
                auth=auth,
                id=cat_id,
                data={
                    'nested_categories': new_sub_cats
                },
            )
            # Add the staged change to the staging DB
            self._staged.add(staged_change)

    def delete_sub_category(self, auth: AuthUser, cat_id: str, sub_cat_id: str) -> None:
        # Get current sub-categories
        current_sub_cats = self.get_sub_categories_by_id(cat_id)

        # Remove the sub-category if it exists
        if sub_cat_id in current_sub_cats:
            new_sub_cats = [c for c in current_sub_cats if c != sub_cat_id]

            # Create a staged change for the CATEGORY table
            staged_change = StagedChange(
                type=StagedChangeAction.UPDATE,
                table=StagedChangeTable.CATEGORY,
                auth=auth,
                id=cat_id,
                data={
                    'nested_categories': new_sub_cats
                },
            )
            # Add the staged change to the staging DB
            self._staged.add(staged_change)

    def set_sub_categories(self, auth: AuthUser, cat_id: str, cat_ids: List[str]) -> None:
        # Create a staged change for the CATEGORY table with the new nested_categories
        staged_change = StagedChange(
            type=StagedChangeAction.UPDATE,
            table=StagedChangeTable.CATEGORY,
            auth=auth,
            id=cat_id,
            data={
                'nested_categories': cat_ids
            },
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

    def commit(self, change: StagedChange) -> None:
        # This is no longer needed as changes are stored in the CATEGORY table
        # and will be committed by the category_db.py commit method
        pass
