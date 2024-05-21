class AuditlogDB:
    def __init__(self, conn):
        self.conn = conn
        self.create_Table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS commit_log (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reverted BOOLEAN DEFAULT 0
        );''')
        self.conn.commit()

    def revert_commit(self, commit_id):
        # find all changes and revert them
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM change_log WHERE commit_id = ?', commit_id)
        changes = cursor.fetchall()

        # we revert every change in reverse, from latest to oldest
        for row in changes[::-1]:
            TokenCategoriesDB.revert_change(change.id)
