-- Migration script: 4_category_constraints.sql
-- Add UNIQUE INDEX to sub_category, token_categories, and url_categories
-- prevents multiple pairs of (<obj> - categories - is_deleted) to exist

-- Step 1: Add UNIQUE INDEX to sub_category
CREATE UNIQUE INDEX IF NOT EXISTS unique_parent_child_deleted ON sub_category (parent_id, child_id, is_deleted);

-- Step 2: Add UNIQUE INDEX to token_categories
CREATE UNIQUE INDEX IF NOT EXISTS unique_token_category_deleted ON token_categories (token_id, category_id, is_deleted);

-- Step 3: Add UNIQUE INDEX to url_categories
CREATE UNIQUE INDEX IF NOT EXISTS unique_url_category_deleted ON url_categories (url_id, category_id, is_deleted);

-- Insert records to mark the migration
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added UNIQUE INDEX to sub_category table', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added UNIQUE INDEX to token_categories table', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Added UNIQUE INDEX to url_categories table', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Migrated DB to version: 4', 'system');
