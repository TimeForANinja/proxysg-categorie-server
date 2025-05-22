import time
from dataclasses import asdict
from typing import Optional, List, Dict, Any
import uuid

from auth.auth_user import AuthUser
from db.abc.category import MutableCategory, Category
from db.abc.db import DBInterface
from db.stagingdb.cache import StagedChange, StagedChangeAction, StagedCollection, StagedChangeTable, StageFilter


class StagingDBCategory:
    def __init__(self, db: DBInterface, staged: StagedCollection):
        self._db = db
        self._staged = staged

    def add_category(self, auth: AuthUser, category: MutableCategory) -> Category:
        category_id = str(uuid.uuid4())
        category_data = asdict(category)
        category_data.update({
            'id': category_id,
        })

        # Create a staged change
        staged_change = StagedChange(
            action_type=StagedChangeAction.ADD,
            table=StagedChangeTable.CATEGORY,
            auth=auth,
            uid=category_id,
            data=category_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        # Create a Category object to return
        return Category(**category_data)

    def get_category(self, category_id: str) -> Optional[Category]:
        # try getting it from the database
        db_category: Category = self._db.categories.get_category(category_id)
        # convert to dict
        category: Dict[str, Any] = asdict(db_category) if db_category is not None else None

        if category is None:
            # no category in DB, so check if we have an "add" event
            add_category = self._staged.first_or_none(
                StageFilter.fac_filter_table_id(StagedChangeTable.CATEGORY, category_id),
                StageFilter.filter_add,
            )
            category = add_category.data if add_category is not None else None

        # overload any staged changes
        for staged_change in self._staged.iter_filter(
                StageFilter.fac_filter_table_id(StagedChangeTable.CATEGORY, category_id),
        ):
            if staged_change.data.get('is_deleted', 0) != 0:
                return None

            category.update(staged_change.data)

        return Category(**category)

    def update_category(self, auth: AuthUser, cat_id: str, category: MutableCategory) -> Category:
        update_data = asdict(category)

        # Create a staged change
        staged_change = StagedChange(
            action_type=StagedChangeAction.UPDATE,
            table=StagedChangeTable.CATEGORY,
            auth=auth,
            uid=cat_id,
            data=update_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        return self.get_category(cat_id)

    def delete_category(self, auth: AuthUser, cat_id: str) -> None:
        update_data = {'is_deleted': int(time.time())}

        # Create a staged change
        staged_change = StagedChange(
            action_type=StagedChangeAction.DELETE,
            table=StagedChangeTable.CATEGORY,
            auth=auth,
            uid=cat_id,
            data=update_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        return self.get_category(cat_id)

    def get_all_categories(self) -> List[Category]:
        # Get all categories from the database
        db_categories: List[Category] = self._db.categories.get_all_categories()
        # convert to dict
        categories: List[Dict[str, Any]] = [asdict(category) for category in db_categories]

        # append all "added" categories from the cache
        categories.extend(
            [
                c.data for c in
                self._staged.iter_filter(
                    StageFilter.filter_add,
                    StageFilter.fac_filter_table(StagedChangeTable.CATEGORY),
                )
            ]
        )

        staged_categories: List[Category] = []

        for raw_category in categories:
            category = raw_category

            # overload any staged changes
            for staged_change in self._staged.iter_filter(
                StageFilter.fac_filter_table_id(StagedChangeTable.CATEGORY, category.get('id'))
            ):
                category.update(staged_change.data)

            if category.get('is_deleted', 0) == 0:
                staged_categories.append(Category(**category))

        return staged_categories

    def commit(self, change: StagedChange) -> None:
        # TODO: implement
        pass
