-- Migration script: 2_add_user_column.sql
-- Add user column to history table

-- Step 1: Add a new column, initially allowing NULLs
ALTER TABLE history ADD COLUMN new_user TEXT;

-- Step 2: Set the new column to 'system' where it is currently NULL
UPDATE history SET new_user = 'system' WHERE new_user IS NULL;

-- Step 3: Create a new table with the desired column constraints
-- Replace 'new_user' with 'user' and enforce NOT NULL
CREATE TABLE history_new (
    id INTEGER PRIMARY KEY,
    time INTEGER NOT NULL,
    description TEXT NOT NULL,
    user TEXT NOT NULL
);

-- Step 4: Copy the data from the old table to the new table
INSERT INTO history_new (id, time, description, user)
SELECT id, time, description, new_user
FROM history;

-- Step 5: Drop the old table
DROP TABLE history;

-- Step 6: Rename the new table to the original table name
ALTER TABLE history_new RENAME TO history;

-- Insert records to mark the migration
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added user column to history table', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Migrated DB to version: 2', 'system');
