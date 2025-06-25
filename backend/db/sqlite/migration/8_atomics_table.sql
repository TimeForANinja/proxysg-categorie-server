-- Migration script: 8_atomics_table.sql
-- Add atomics table for storing atomic changes within history events

-- Step 1: Create the atomics table
CREATE TABLE IF NOT EXISTS atomics (
    id INTEGER PRIMARY KEY,
    user TEXT NOT NULL,
    history_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    description TEXT NOT NULL,
    ref_token TEXT NOT NULL DEFAULT '',
    ref_url TEXT NOT NULL DEFAULT '',
    ref_category TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (history_id) REFERENCES history(id)
);

-- Insert records to mark the migration
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added atomics table', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Migrated DB to version: 8', 'system');