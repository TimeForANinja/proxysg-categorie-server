import time
from typing import Optional, List

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.backend.abc.util.types import MyTransactionType
from db.dbmodel.history import Atomic
from db.dbmodel.staging import ActionType, ActionTable, StagedChange
from db.dbmodel.url import MutableURL, URL
from db.middleware.abc.url_db import MiddlewareDBURL
from db.middleware.stagingdb.cache import StagedCollection
from db.middleware.stagingdb.utils.add_uid import add_uid_to_object, add_uid_to_objects
from db.middleware.stagingdb.utils.cache import SessionCache
from db.middleware.stagingdb.utils.overloading import add_staged_change, get_and_overload_object, \
    get_and_overload_all_objects, add_staged_changes, update_dataclass
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

    def add_urls(self, auth: AuthUser, mut_urls: List[MutableURL]) -> List[URL]:
        if not mut_urls:
            return []

        # Generate a UUID and add it to the URL data
        url_ids, url_data = add_uid_to_objects(mut_urls)

        add_staged_changes(
            action_type=ActionType.ADD,
            action_table=ActionTable.URL,
            auth=auth,
            obj_ids=url_ids,
            update_data=url_data,
            staged=self._staged,
        )

        # Create a list of URL objects to return
        resp = []
        for ud in url_data:
            ud.update({'pending_changes': True})
            resp.append(URL(**ud))
        return resp

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
            update_data=mut_url.__dict__,
            staged=self._staged,
        )

        return self.get_url(url_id)

    def set_bc_cats(self, url_id: str, bc_cats: List[str]):
        # BC cats updates go straight to DB
        return self._db.urls.set_bc_cats(url_id, bc_cats)

    def delete_url(self, auth: AuthUser, url_id: str):
        add_staged_change(
            action_type=ActionType.DELETE,
            action_table=ActionTable.URL,
            auth=auth,
            obj_id=url_id,
            update_data={'is_deleted': int(time.time())},
            staged=self._staged,
        )

    def get_all_urls(self, bypass_cache: bool = False) -> List[URL]:
        if bypass_cache:
            return self._db.urls.get_all_urls()

        return get_and_overload_all_objects(
            db_getter=self._db.urls.get_all_urls,
            staged=self._staged,
            action_table=ActionTable.URL,
            obj_class=URL
        )

    def commit(
        self,
        change: StagedChange,
        cache: SessionCache,
        dry_run: bool,
        session: Optional[MyTransactionType] = None,
    ) -> Optional[Atomic]:
        """
        Apply the staged change to the persistent database.

        :param change: The staged change to apply.
        :param cache: A Cache for requests against the Database
        :param dry_run: Whether to perform a dry run (no changes are made to the database). Default is False.
        :param session: Optional database session to use
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
                self._db.urls.add_url(mutable_url, url_id, session=session)

            # add URL to the cache for future requests
            cache.update_url(
                URL.from_mutable(url_id, mutable_url)
            )

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
                self._db.urls.update_url(change.uid, mutable_url, session=session)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Update",
                description=f"Updated URL {url_data.get('hostname')}",
                ref_url=[change.uid],
            )
        elif change.action_type == ActionType.SET_CATS:
            url_data = change.data.copy()

            current_url = cache.get_url(change.uid)

            # Update the token in the persistent database
            added, removed = set_categories(
                current_url.categories if current_url else [],
                url_data['categories'],
                lambda cid: self._db.url_categories.add_url_category(change.uid, cid, session=session),
                lambda cid: self._db.url_categories.delete_url_category(change.uid, cid, change.timestamp, session=session),
                dry_run,
            )
            # update cached URL for future requests
            cache.update_url(
                update_dataclass(current_url, {'categories': url_data['categories']}, URL)
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
                self._db.urls.delete_url(change.uid, change.timestamp, session=session)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Delete",
                description=f"Deleted URL {change.data.get('hostname')}",
                ref_url=[change.uid],
            )

        # Unknown action_type
        return None
