from typing import Optional, Iterator, Callable

from db.backend.abc.db import DBInterface
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

    def iter(self) -> Iterator[StagedChange]:
        """Iterate through all staged changes."""
        # Get all staged changes from the persistent storage
        changes = self._db.staging.get_staged_changes()
        return iter(changes)

    def iter_filter(self, *conditions: Callable[[StagedChange], bool]) -> Iterator[StagedChange]:
        """Iterate through staged changes that match the given conditions."""
        iterator = self.iter()
        for c in conditions:
            iterator = filter(c, iterator)
        return iterator

    def first_or_none(self, *conditions: Callable[[StagedChange], bool]) -> Optional[StagedChange]:
        """Get the first staged change that matches the given conditions, or "None" if none match."""
        return next(self.iter_filter(*conditions), None)

    def remove(self, change: StagedChange):
        """Remove a staged change from the persistent storage."""
        # This is a bit tricky since we don't have a direct way to remove a specific change.
        # For now, we'll get all changes, filter out the one we want to remove, and clear and re-add the rest

        # Filter out the change we want to remove
        filtered_changes = [c for c in self.iter() if not (
                c.action_type == change.action_type and
                c.action_table == change.action_table and
                c.uid == change.uid and
                c.auth.username == change.auth.username
        )]

        # Clear all changes
        self.clear()

        # Re-add the filtered changes
        for c in filtered_changes:
            self.add(c)

    def clear(self):
        """Clear all staged changes from the persistent storage."""
        self._db.staging.clear_staged_changes()

    def simplify_stack(self):
        """Simplify the stack of staged changes."""
        # This is handled by the database, so we don't need to do anything here
        pass

class StageFilter:
    @staticmethod
    def filter_add(change: StagedChange) -> bool:
        return change.action_type == ActionType.ADD

    @staticmethod
    def fac_filter_table(table: ActionTable) -> Callable[[StagedChange], bool]:
        return lambda change: change.action_table == table

    @staticmethod
    def fac_filter_id(uid: str) -> Callable[[StagedChange], bool]:
        return lambda change: change.uid == uid

    @staticmethod
    def fac_filter_table_id(table: ActionTable, uid: str) -> Callable[[StagedChange], bool]:
        return lambda change: change.action_table == table and change.uid == uid
