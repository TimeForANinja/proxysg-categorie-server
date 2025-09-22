from typing import List, Tuple

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.dbmodel.staging import ActionType, ActionTable
from db.middleware.abc.url_category_db import MiddlewareDBURLCategory
from db.middleware.stagingdb.cache import StagedCollection
from db.middleware.stagingdb.url_db import StagingDBURL
from db.middleware.stagingdb.utils.overloading import add_staged_change, add_staged_changes


class StagingDBURLCategory(MiddlewareDBURLCategory):
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

    def add_url_categories(self, auth: AuthUser, mappings: List[Tuple[str, str]]) -> None:
        if not mappings:
            return

        # reformat into a map of url_id to category_ids
        unique_urls = set([x[1] for x in mappings])

        # get a list of all URL
        known_urls = self._url_db.get_all_urls()

        url_ids = []
        url_cat_data = []
        for url_id in unique_urls:
            # TODO: check if the url validation is needed
            # identify url
            url_item = next((x for x in known_urls if x.id == url_id), None)
            if url_item is None:
                raise Exception(f"URL {url_id} not found")

            new_cats = [x[0] for x in mappings if x[1] == url_id]
            # convert to set to deduplicate
            total_cats = list(set(new_cats + url_item.categories))
            # push to global lists, later used for creating staged changes
            url_ids.append(url_id)
            url_cat_data.append({ 'categories': total_cats })

        # Use stage_update to create and add the staged change
        # TODO: check if we can use "ADD" instead of "SET" to simplify the code
        add_staged_changes(
            action_type=ActionType.SET_CATS,
            action_table=ActionTable.URL,
            auth=auth,
            obj_ids=url_ids,
            update_data=url_cat_data,
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
