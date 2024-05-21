class AuditlogDB:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS change_log (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            operation TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER,
            old_data TEXT,
            new_data TEXT,
            commit_id INTEGER,
            FOREIGN KEY (commit_id) REFERENCES commit_log(id),
        );''')
        self.conn.commit()

    def revert_change(self, change_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT operation, table_name, record_id, old_data, new_data FROM audit_log WHERE id = ? AND reverted = 0', (change_id,))
        change = cursor.fetchone()

        if not change:
            # Change not found or already reverted
            return False

        operation, table_name, record_id, old_data, new_data = change

        if operation == 'insert':
            cursor.execute('DELETE FROM ? WHERE id = ?', (table_name, record_id))
        elif operation == 'update':
            cursor.execute('UPDATE ? SET ? WHERE id = ?', (table_name, old_data, record_id))
        elif operation == 'delete':
            cursor.execute('INSERT INTO ? VALUES ?', (table_name, new_data))

        # Mark the change as reverted
        cursor.execute('UPDATE audit_log SET reverted = 1 WHERE id = ?', (change_id,))
        self.conn.commit()

        return True
