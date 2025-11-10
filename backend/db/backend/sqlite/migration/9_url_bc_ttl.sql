-- Migration script: 9_url_bc_ttl.sql
-- Add a new row to URLs table to track last time the BC Cats were fetched

-- Step 1: Add a new column, defaulting to value "0"
ALTER TABLE urls ADD COLUMN bc_last_set INTEGER NOT NULL default 0;

-- Insert records to mark the migration
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Migrated DB to version: 9', '{"username": "system", "roles": []}');
