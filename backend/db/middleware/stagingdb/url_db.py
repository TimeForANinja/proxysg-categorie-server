import time
from dataclasses import asdict
from typing import Optional, List

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.dbmodel.history import Atomic
from db.dbmodel.staging import ActionType, ActionTable, StagedChange
from db.dbmodel.url import MutableURL, URL
from db.middleware.abc.url_db import MiddlewareDBURL
from db.middleware.stagingdb.cache import StagedCollection
from db.middleware.stagingdb.utils.add_uid import add_uid_to_object
from db.middleware.stagingdb.utils.overloading import add_staged_change, get_and_overload_object, get_and_overload_all_objects
from db.middleware.stagingdb.utils.update_cats import set_categories


class StagingDBURL(MiddlewareDBURL):
    def __init__(self, db: DBInterface, staged: StagedCollection):
        self._db = db
        self._staged = staged

    def add_url(self, auth: AuthUser, mut_url: MutableURL) -> URL:
        # Generate a UUID and add it to the URL data
        url_id, url_data = add_uid_to_object(mut_url)

        add_staged_change(
            action_type=ActionType.ADD,
            action_table=ActionTable.URL,
            auth=auth,
            obj_id=url_id,
            update_data=url_data,
            staged=self._staged,
        )

        # Create a URL object to return
        url_data.update({'pending_changes': True})
        return URL(**url_data)

    def get_url(self, url_id: str) -> Optional[URL]:
        return get_and_overload_object(
            db_getter=self._db.urls.get_url,
            staged=self._staged,
            action_table=ActionTable.URL,
            obj_id=url_id,
            obj_class=URL
        )

    def update_url(self, auth: AuthUser, url_id: str, mut_url: MutableURL) -> URL:
        add_staged_change(
            action_type=ActionType.UPDATE,
            action_table=ActionTable.URL,
            auth=auth,
            obj_id=url_id,
            update_data=asdict(mut_url),
            staged=self._staged,
        )

        return self.get_url(url_id)

    def set_bc_cats(self, url_id: str, bc_cats: List[str]) -> None:
        # BC cats updates go straight to DB
        return self._db.urls.set_bc_cats(url_id, bc_cats)

    def delete_url(self, auth: AuthUser, url_id: str) -> None:
        add_staged_change(
            action_type=ActionType.DELETE,
            action_table=ActionTable.URL,
            auth=auth,
            obj_id=url_id,
            update_data={'is_deleted': int(time.time())},
            staged=self._staged,
        )

    def get_all_urls(self) -> List[URL]:
        return get_and_overload_all_objects(
            db_getter=self._db.urls.get_all_urls,
            staged=self._staged,
            action_table=ActionTable.URL,
            obj_class=URL
        )

    def commit(self, change: StagedChange, dry_run: bool) -> Optional[Atomic]:
        """
        Apply the staged change to the persistent database.

        :param change: The staged change to apply.
        :param dry_run: Whether to perform a dry run (no changes are made to the database). Default is False.
        :return: The atomic operation that was applied to the database.
        """
        if change.action_table != ActionTable.URL:
            return None

        # Apply the change to the persistent database based on the action type
        if change.action_type == ActionType.ADD:
            # Create a MutableURL from the data
            url_data = change.data.copy()
            url_id = url_data.pop('id')
            mutable_url = MutableURL(**url_data)

            if not dry_run:
                # Add the URL to the persistent database
                self._db.urls.add_url(mutable_url, url_id)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Add",
                description=f"Added URL {url_data.get('hostname')}",
                ref_url=[url_id],
            )
        elif change.action_type == ActionType.UPDATE:
            # Create a MutableURL from the data
            url_data = change.data.copy()
            mutable_url = MutableURL(**url_data)

            if not dry_run:
                # Update the URL in the persistent database
                self._db.urls.update_url(change.uid, mutable_url)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Update",
                description=f"Updated URL {url_data.get('hostname')}",
                ref_url=[change.uid],
            )
        elif change.action_type == ActionType.SET_CATS:
            url_data = change.data.copy()

            current_cats = self._db.urls.get_url(change.uid)

            # Update the token in the persistent database
            added, removed = set_categories(
                current_cats.categories if current_cats else [],
                url_data['categories'],
                lambda cid: self._db.url_categories.add_url_category(change.uid, cid),
                lambda cid: self._db.url_categories.delete_url_category(change.uid, cid),
                dry_run,
            )

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Set Categories",
                description=f"Updated Categories for URL {url_data.get('hostname')}, added {added}, removed {removed}",
                ref_url=[change.uid],
            )
        elif change.action_type == ActionType.DELETE:
            if not dry_run:
                # Delete the URL from the persistent database
                self._db.urls.delete_url(change.uid)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Delete",
                description=f"Deleted URL {change.data.get('hostname')}",
                ref_url=[change.uid],
            )

        # Unknown action_type
        return None
