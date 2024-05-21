class VersionControl:
    def __init__(self):
        self.pending_changes = []  # Track changes made within the session
        self.commits = []  # Track committed changes

    def add_change(self, change):
        self.pending_changes.append(change)

    def commit_changes(self):
        # Create a new commit containing pending changes
        commit_id = len(self.commits) + 1
        commit = {"id": commit_id, "changes": self.pending_changes.copy()}
        self.commits.append(commit)
        self.pending_changes = []  # Clear pending changes after committing
        return commit_id

    def revert_to_commit(self, commit_id):
        if commit_id <= 0 or commit_id > len(self.commits):
            return False  # Invalid commit ID

        # Revert changes made after the specified commit
        for i in range(commit_id, len(self.commits)):
            commit = self.commits[i]
            for change in reversed(commit["changes"]):
                # Undo the change
                self.undo_change(change)

        # Remove commits after the specified commit
        self.commits = self.commits[:commit_id]

        return True

    def undo_change(self, change):
        operation, table_name, record_id, old_data, new_data = change

        if operation == 'insert':
            # Delete the inserted record
            cursor.execute('DELETE FROM ? WHERE id = ?', (table_name, record_id))
        elif operation == 'update':
            # Revert the update by setting the record back to its old state
            cursor.execute('UPDATE ? SET ? WHERE id = ?', (table_name, old_data, record_id))
        elif operation == 'delete':
            # Re-insert the deleted record
            cursor.execute('INSERT INTO ? VALUES ?', (table_name, new_data))

        self.conn.commit()
