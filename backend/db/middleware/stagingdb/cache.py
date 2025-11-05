from typing import Callable, List, Optional

from db.backend.abc.db import DBInterface
from db.backend.abc.util.types import MyTransactionType
from db.dbmodel.staging import StagedChange, ActionType, ActionTable


class StagedCollection:
    """
    A persistent implementation of StagedCollection that uses a StagingDBInterface
    to store staged changes in a persistent database.
    """

    def __init__(self, db: DBInterface):
        self._db = db

    def add(self, change: StagedChange):
        """Add a staged change to the persistent storage."""
        # Store the change in the persistent storage
        self._db.staging.store_staged_change(change)
        self.simplify_stack()

    def add_batch(self, changes: List[StagedChange]):
        """Add a list of staged changes to the persistent storage."""
        if not changes:
            return

        # Store the change in the persistent storage
        self._db.staging.store_staged_changes(changes)
        self.simplify_stack()

    def get_all(self, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        """Get all staged changes from the persistent storage."""
        return self._db.staging.get_staged_changes(session=session)

    def get_filtered(self, *filters: Callable[[List[StagedChange]], List[StagedChange]]) -> List[StagedChange]:
        """Get all staged changes that match the given conditions."""
        return StageFilter.apply(self.get_all(), *filters)

    def remove(self, change: StagedChange):
        """Remove a staged change from the persistent storage."""
        # TODO: implement proper removal
        # This is a bit tricky since we don't have a direct way to remove a specific change.
        # For now, we'll get all changes, filter out the one we want to remove, and clear and re-add the rest

        # Filter out the change we want to remove
        filtered_changes = [c for c in self.get_all() if not (
                c.action_type == change.action_type and
                c.action_table == change.action_table and
                c.uid == change.uid and
                c.auth.username == change.auth.username
        )]

        # Clear all changes
        self.clear()

        # Re-add the filtered changes
        self.add_batch(filtered_changes)

    def clear(self, before: int = None, session: Optional[MyTransactionType] = None):
        """
        Clear all staged changes from the persistent storage.

        :param before: The timestamp before which to clear changes.
        :param session: The database session to use.
        """
        self._db.staging.clear_staged_changes(before=before, session=session)

    def simplify_stack(self):
        """Simplify the stack of staged changes."""
        # This is handled by the database, so we don't need to do anything here
        pass


class StageFilter:
    @staticmethod
    def apply(changes: List[StagedChange], *filters: Callable[[List[StagedChange]], List[StagedChange]]) -> List[StagedChange]:
        filtered = changes
        for f in filters:
            filtered = f(filtered)
        return filtered

    @staticmethod
    def first_or_default(
            changes: List[StagedChange],
            *filters: Callable[[List[StagedChange]], List[StagedChange]],
            default: Optional[StagedChange]=None,
    ) -> Optional[StagedChange]:
        filtered = StageFilter.apply(changes, *filters)
        # return the first element, or the "default" if none was left
        if len(filtered) > 0:
            return changes[0]
        else:
            return default

    @staticmethod
    def filter_add(changes: List[StagedChange]) -> List[StagedChange]:
        return [
            change
            for change in changes
            if change.action_type == ActionType.ADD
        ]

    @staticmethod
    def fac_filter_table(table: ActionTable) -> Callable[[List[StagedChange]], List[StagedChange]]:
        return lambda changes: [
            change
            for change in changes
            if change.action_table == table
        ]

    @staticmethod
    def fac_filter_id(uid: str) -> Callable[[List[StagedChange]], List[StagedChange]]:
        return lambda changes: [
            change
            for change in changes
            if change.uid == uid
        ]

    @staticmethod
    def fac_filter_table_id(table: ActionTable, uid: str) -> Callable[[List[StagedChange]], List[StagedChange]]:
        return lambda changes: [
            change
            for change in changes
            if change.action_table == table and change.uid == uid
        ]
