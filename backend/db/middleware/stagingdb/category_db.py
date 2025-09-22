import time
from dataclasses import asdict
from typing import Optional, List

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.dbmodel.category import MutableCategory, Category
from db.dbmodel.history import Atomic
from db.dbmodel.staging import ActionType, ActionTable, StagedChange
from db.middleware.abc.category_db import MiddlewareDBCategory
from db.middleware.stagingdb.cache import StagedCollection
from db.middleware.stagingdb.utils.add_uid import add_uid_to_object, add_uid_to_objects
from db.middleware.stagingdb.utils.overloading import add_staged_change, add_staged_changes, get_and_overload_object, get_and_overload_all_objects
from db.middleware.stagingdb.utils.update_cats import set_categories


class StagingDBCategory(MiddlewareDBCategory):
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
        category_data.update({'pending_changes': True})
        return Category(**category_data)

    def add_categories(self, auth: AuthUser, categories: List[MutableCategory]) -> List[Category]:
        if not categories:
            return []

        # Generate a UUID and add it to the category data
        cat_ids, cat_data = add_uid_to_objects(categories)

        add_staged_changes(
            action_type=ActionType.ADD,
            action_table=ActionTable.CATEGORY,
            auth=auth,
            obj_ids=cat_ids,
            update_data=cat_data,
            staged=self._staged,
        )

        # Create a list of Category objects to return
        resp = []
        for cd in cat_data:
            cd.update({'pending_changes': True})
            resp.append(Category(**cd))
        return resp

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

    def commit(self, change: StagedChange, dry_run: bool) -> Optional[Atomic]:
        """
        Apply the staged change to the persistent database.

        :param change: The staged change to apply.
        :param dry_run: Whether to perform a dry run (no changes are made to the database). Default is False.
        :return: The atomic operation that was applied to the database.
        """
        if change.action_table != ActionTable.CATEGORY:
            return None

        # Apply the change to the persistent database based on the action type
        if change.action_type == ActionType.ADD:
            # Create a MutableCategory from the data
            category_data = change.data.copy()
            category_id = category_data.pop('id')
            mutable_category = MutableCategory(**category_data)

            if not dry_run:
                # Add the category to the persistent database
                self._db.categories.add_category(mutable_category, category_id)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Add",
                description=f"Added category {category_data.get('name')}",
                ref_category=[category_id],
            )
        elif change.action_type == ActionType.UPDATE:
            # Create a MutableCategory from the data
            category_data = change.data.copy()
            mutable_category = MutableCategory(**category_data)

            if not dry_run:
                # Update the category in the persistent database
                self._db.categories.update_category(change.uid, mutable_category)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Update",
                description=f"Updated category {category_data.get('name')}",
                ref_category=[change.uid],
            )
        elif change.action_type == ActionType.SET_CATS:
            category_data = change.data.copy()

            current_cats = self._db.categories.get_category(change.uid)

            # Update the category mappings in the persistent database
            added, removed = set_categories(
                current_cats.nested_categories if current_cats else [],
                category_data['nested_categories'],
                lambda cid: self._db.sub_categories.add_sub_category(change.uid, cid),
                lambda cid: self._db.sub_categories.delete_sub_category(change.uid, cid),
                dry_run,
            )

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Set Categories",
                description=f"Updated sub-categories for category {category_data.get('name')}, added {added}, removed {removed}",
                ref_category=[change.uid],
            )
        elif change.action_type == ActionType.DELETE:
            if not dry_run:
                # Delete the category from the persistent database
                self._db.categories.delete_category(change.uid)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Delete",
                description=f"Deleted category {change.data.get('name')}",
                ref_category=[change.uid],
            )

        # Unknown action_type
        return None
