from typing import List, Optional

from db.backend.abc.db import DBInterface
from db.backend.abc.util.types import MyTransactionType
from db.dbmodel.staging import StagedChange, ActionTable


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

    def get_by_table(self, table: ActionTable, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        """Get all staged changes from a specific table."""
        return self._db.staging.get_staged_changes_by_table(table, session=session)

    def get_by_table_and_id(self, table: ActionTable, obj_id: str, session: Optional[MyTransactionType] = None) -> List[StagedChange]:
        """Get all staged changes from a specific table and object ID."""
        return self._db.staging.get_staged_changes_by_table_and_id(table, obj_id, session=session)

    def remove(self, change: StagedChange):
        """Remove a staged change from the persistent storage."""
        # TODO: implement proper removal & use sessions
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
