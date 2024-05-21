class CategoriesDB:
    # Existing methods...

    def add_category(self, name):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        self.conn.commit()
        lastrowid = cursor.lastrowid
        
        # Log the change
        cursor.execute('INSERT INTO change_log (operation, table_name, record_id, new_data) VALUES (?, ?, ?, ?)',
                       ('insert', 'categories', lastrowid, f'{{"name": "{name}"}}'))
        self.conn.commit()

        return lastrowid

    def update_category(self, category_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM categories WHERE id = ?', (category_id,))
        old_name = cursor.fetchone()[0]

        cursor.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, category_id))
        self.conn.commit()
        
        # Log the change
        cursor.execute('INSERT INTO change_log (operation, table_name, record_id, old_data, new_data) VALUES (?, ?, ?, ?, ?)',
                       ('update', 'categories', category_id, f'{{"name": "{old_name}"}}', f'{{"name": "{new_name}"}}'))
        self.conn.commit()

    def delete_category(self, category_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM categories WHERE id = ?', (category_id,))
        name = cursor.fetchone()[0]

        cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        self.conn.commit()
        
        # Log the change
        cursor.execute('INSERT INTO change_log (operation, table_name, record_id, old_data) VALUES (?, ?, ?, ?)',
                       ('delete', 'categories', category_id, f'{{"name": "{name}"}}'))
        self.conn.commit()
