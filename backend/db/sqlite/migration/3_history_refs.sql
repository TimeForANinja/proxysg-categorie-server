-- Migration script: 3_history_refs.sql
-- Add columns for ref_token, ref_url and ref_category

-- Step 1: Add new columns - initialize missing values to default (empty string)
ALTER TABLE history ADD COLUMN ref_token TEXT NOT NULL DEFAULT '';
ALTER TABLE history ADD COLUMN ref_url TEXT NOT NULL DEFAULT '';
ALTER TABLE history ADD COLUMN ref_category TEXT NOT NULL DEFAULT '';

-- Insert records to mark the migration
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added ref_token column to history table', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added ref_url column to history table', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added ref_category column to history table', 'system');
