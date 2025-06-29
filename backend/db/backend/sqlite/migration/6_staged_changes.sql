-- Migration script: 6_staged_changes.sql
-- Add a new table to track staged (atomic) changes

-- Step 1: Create the new staged_changes table
CREATE TABLE IF NOT EXISTS staged_changes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	action TEXT NOT NULL,
    user TEXT NOT NULL,
    timestamp INTEGER,
	table_name TEXT NOT NULL,
	entity_id TEXT,
	data TEXT
);

-- Insert records to mark the migration
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Created Table staged_changes', '{"username": "system", "roles": []}');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Migrated DB to version: 6', '{"username": "system", "roles": []}');
