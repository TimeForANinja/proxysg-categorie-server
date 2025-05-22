import time
from dataclasses import asdict
from typing import Optional, List, Dict, Any
import uuid

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.url import MutableURL, URL
from db.stagingdb.cache import StagedChange, StagedChangeAction, StagedCollection, StagedChangeTable, StageFilter


class StagingDBURL:
    def __init__(self, db: DBInterface, staged: StagedCollection):
        self._db = db
        self._staged = staged

    def add_url(self, auth: AuthUser, mut_url: MutableURL) -> URL:
        url_id = str(uuid.uuid4())
        url_data = asdict(mut_url)
        url_data.update({
            'id': url_id,
        })

        # Create a staged change
        staged_change = StagedChange(
            action_type=StagedChangeAction.ADD,
            table=StagedChangeTable.URL,
            auth=auth,
            uid=url_id,
            data=url_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        # Create a URL object to return
        return URL(**url_data)

    def get_url(self, url_id: str) -> Optional[URL]:
        # try getting it from the database
        db_url: URL = self._db.urls.get_url(url_id)
        # convert to dict
        url: Dict[str, Any] = asdict(db_url) if db_url is not None else None

        if url is None:
            # no url in DB, so check if we have an "add" event
            add_url = self._staged.first_or_none(
                StageFilter.fac_filter_table_id(StagedChangeTable.URL, url_id),
                StageFilter.filter_add,
            )
            url = add_url.data if add_url is not None else None

        # overload any staged changes
        for staged_change in self._staged.iter_filter(
                StageFilter.fac_filter_table_id(StagedChangeTable.URL, url_id),
        ):
            if staged_change.data.get('is_deleted', 0) != 0:
                return None

            url.update(staged_change.data)

        return URL(**url)

    def update_url(self, auth: AuthUser, url_id: str, mut_url: MutableURL) -> URL:
        update_data = asdict(mut_url)

        # Create a staged change
        staged_change = StagedChange(
            action_type=StagedChangeAction.UPDATE,
            table=StagedChangeTable.URL,
            auth=auth,
            uid=url_id,
            data=update_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        return self.get_url(url_id)

    def set_bc_cats(self, url_id: str, bc_cats: List[str]) -> None:
        # BC cats updates go straight to DB
        return self._db.urls.set_bc_cats(url_id, bc_cats)

    def delete_url(self, auth: AuthUser, url_id: str) -> None:
        update_data = {'is_deleted': int(time.time())}

        # Create a staged change
        staged_change = StagedChange(
            action_type=StagedChangeAction.DELETE,
            table=StagedChangeTable.URL,
            auth=auth,
            uid=url_id,
            data=update_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        return self.get_url(url_id)

    def get_all_urls(self) -> List[URL]:
        # Get all urls from the database
        db_urls: List[URL] = self._db.urls.get_all_urls()
        # convert to dict
        urls: List[Dict[str, Any]] = [asdict(url) for url in db_urls]

        # append all "added" urls from the cache
        urls.extend(
            [
                u.data for u in
                self._staged.iter_filter(
                    StageFilter.filter_add,
                    StageFilter.fac_filter_table(StagedChangeTable.URL),
                )
            ]
        )

        staged_urls: List[URL] = []

        for raw_url in urls:
            url = raw_url

            # overload any staged changes
            for staged_change in self._staged.iter_filter(
                StageFilter.fac_filter_table_id(StagedChangeTable.URL, url.get('id'))
            ):
                url.update(staged_change.data)

            if url.get('is_deleted', 0) == 0:
                staged_urls.append(URL(**url))

        return staged_urls

    def commit(self, change: StagedChange) -> None:
        """
        Apply the staged change to the persistent database.

        :param change: The staged change to apply.
        """
        if change.table != StagedChangeTable.URL:
            return

        # Apply the change to the persistent database based on the action type
        if change.type == StagedChangeAction.ADD:
            # Create a MutableURL from the data
            url_data = change.data.copy()
            url_id = url_data.pop('id')
            mutable_url = MutableURL(**url_data)

            # Add the URL to the persistent database
            self._db.urls.add_url(mutable_url, url_id)

            # Create a history event
            self._db.history.add_history_event(
                action=f"Added URL {url_data.get('url')}",
                user=change.auth,
                ref_token=[],
                ref_url=[url_id],
                ref_category=[],
            )
        elif change.type == StagedChangeAction.UPDATE:
            # Create a MutableURL from the data
            url_data = change.data.copy()
            mutable_url = MutableURL(**url_data)

            # Update the URL in the persistent database
            self._db.urls.update_url(change.id, mutable_url)

            # Create a history event
            self._db.history.add_history_event(
                action=f"Updated URL {url_data.get('url')}",
                user=change.auth,
                ref_token=[],
                ref_url=[change.id],
                ref_category=[],
            )
        elif change.type == StagedChangeAction.DELETE:
            # Delete the URL from the persistent database
            self._db.urls.delete_url(change.id)

            # Create a history event
            self._db.history.add_history_event(
                action=f"Deleted URL",
                user=change.auth,
                ref_token=[],
                ref_url=[change.id],
                ref_category=[],
            )
