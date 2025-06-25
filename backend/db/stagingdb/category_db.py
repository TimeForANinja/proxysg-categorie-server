import time
from dataclasses import asdict
from typing import Optional, List

from auth.auth_user import AuthUser
from db.abc.category import MutableCategory, Category
from db.abc.db import DBInterface
from db.abc.staging import ActionType, ActionTable
from db.stagingdb.cache import StagedChange, StagedCollection
from db.stagingdb.utils.add_uid import add_uid_to_object
from db.stagingdb.utils.overloading import add_staged_change, get_and_overload_object, get_and_overload_all_objects
from db.stagingdb.utils.update_cats import set_categories


class StagingDBCategory:
    def __init__(self, db: DBInterface, staged: StagedCollection):
        self._db = db
        self._staged = staged

    def add_category(self, auth: AuthUser, category: MutableCategory) -> Category:
        # Generate a UUID and add it to the category data
        category_id, category_data = add_uid_to_object(category)

        add_staged_change(
            action_type=ActionType.ADD,
            action_table=ActionTable.CATEGORY,
            auth=auth,
            obj_id=category_id,
            update_data=category_data,
            staged=self._staged,
        )

        # Create a Category object to return
        return Category(**category_data)

    def get_category(self, category_id: str) -> Optional[Category]:
        return get_and_overload_object(
            db_getter=self._db.categories.get_category,
            staged=self._staged,
            action_table=ActionTable.CATEGORY,
            obj_id=category_id,
            obj_class=Category
        )

    def update_category(self, auth: AuthUser, cat_id: str, category: MutableCategory) -> Category:
        add_staged_change(
            action_type=ActionType.UPDATE,
            action_table=ActionTable.CATEGORY,
            auth=auth,
            obj_id=cat_id,
            update_data=asdict(category),
            staged=self._staged,
        )

        return self.get_category(cat_id)

    def delete_category(self, auth: AuthUser, cat_id: str) -> None:
        add_staged_change(
            action_type=ActionType.DELETE,
            action_table=ActionTable.CATEGORY,
            auth=auth,
            obj_id=cat_id,
            update_data={'is_deleted': int(time.time())},
            staged=self._staged,
        )

    def get_all_categories(self) -> List[Category]:
        return get_and_overload_all_objects(
            db_getter=self._db.categories.get_all_categories,
            staged=self._staged,
            action_table=ActionTable.CATEGORY,
            obj_class=Category
        )

    def commit(self, change: StagedChange) -> None:
        """
        Apply the staged change to the persistent database.

        :param change: The staged change to apply.
        """
        if change.action_table != ActionTable.CATEGORY:
            return

        # Apply the change to the persistent database based on the action type
        if change.action_type == ActionType.ADD:
            # Create a MutableCategory from the data
            category_data = change.data.copy()
            category_id = category_data.pop('id')
            mutable_category = MutableCategory(**category_data)

            # Add the category to the persistent database
            self._db.categories.add_category(mutable_category, category_id)

            # Create a history event
            self._db.history.add_history_event(
                action=f"Added category {category_data.get('name')}",
                user=change.auth,
                ref_token=[],
                ref_url=[],
                ref_category=[category_id],
            )
        elif change.action_type == ActionType.UPDATE:
            # Create a MutableCategory from the data
            category_data = change.data.copy()
            mutable_category = MutableCategory(**category_data)

            # Update the category in the persistent database
            self._db.categories.update_category(change.uid, mutable_category)

            # Create a history event
            self._db.history.add_history_event(
                action=f"Updated category {category_data.get('name')}",
                user=change.auth,
                ref_token=[],
                ref_url=[],
                ref_category=[change.uid],
            )
        elif change.action_type == ActionType.SET_CATS:
            category_data = change.data.copy()
            # Update the category mappings in the persistent database
            current_cats = self._db.categories.get_category(change.uid)
            added, removed = set_categories(
                current_cats.nested_categories,
                category_data['nested_categories'],
                lambda cid: self._db.sub_categories.add_sub_category(change.uid, cid),
                lambda cid: self._db.sub_categories.delete_sub_category(change.uid, cid),
            )

            # Create a history event
            self._db.history.add_history_event(
                action=f"Updated sub-categories for category {category_data.get('name')}, added {added}, removed {removed}",
                user=change.auth,
                ref_token=[],
                ref_url=[],
                ref_category=[change.uid],
            )
        elif change.action_type == ActionType.DELETE:
            # Delete the category from the persistent database
            self._db.categories.delete_category(change.uid)

            # Create a history event
            self._db.history.add_history_event(
                action=f"Deleted category",
                user=change.auth,
                ref_token=[],
                ref_url=[],
                ref_category=[change.uid],
            )
