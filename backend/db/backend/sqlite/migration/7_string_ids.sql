-- Migration script: 7_string_ids.sql
-- Convert all ID columns from INTEGER to TEXT

-- Step 1: Create new tables with TEXT IDs

-- Create a new categories table with TEXT IDs
CREATE TABLE categories_new (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    color INTEGER NOT NULL,
    is_deleted INTEGER DEFAULT 0
);

-- Create a new sub_category table with TEXT IDs
CREATE TABLE sub_category_new (
    id INTEGER PRIMARY KEY,
    parent_id TEXT,
    child_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES categories_new(id),
    FOREIGN KEY (child_id) REFERENCES categories_new(id)
);

-- Create a new tokens table with TEXT IDs
CREATE TABLE tokens_new (
    id TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    description TEXT NOT NULL,
    last_use INTEGER DEFAULT 0,
    is_deleted INTEGER DEFAULT 0
);

-- Create a new token_categories table with TEXT IDs
CREATE TABLE token_categories_new (
    id INTEGER PRIMARY KEY,
    token_id TEXT,
    category_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (token_id) REFERENCES tokens_new(id),
    FOREIGN KEY (category_id) REFERENCES categories_new(id)
);

-- Create a new urls table with TEXT IDs
CREATE TABLE urls_new (
    id TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    description TEXT NOT NULL,
    bc_cats TEXT NOT NULL,
    is_deleted INTEGER DEFAULT 0
);

-- Create a new url_categories table with TEXT IDs
CREATE TABLE url_categories_new (
    id INTEGER PRIMARY KEY,
    url_id TEXT,
    category_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (url_id) REFERENCES urls_new(id),
    FOREIGN KEY (category_id) REFERENCES categories_new(id)
);

-- Step 2: Copy data from old tables to new tables, converting IDs to TEXT

-- Copy categories data
INSERT INTO categories_new (id, name, description, color, is_deleted)
SELECT CAST(id AS TEXT), name, description, color, is_deleted
FROM categories;

-- Copy sub_category data
INSERT INTO sub_category_new (id, parent_id, child_id, is_deleted)
SELECT id, CAST(parent_id AS TEXT), CAST(child_id AS TEXT), is_deleted
FROM sub_category;

-- Copy tokens data
INSERT INTO tokens_new (id, token, description, last_use, is_deleted)
SELECT CAST(id AS TEXT), token, description, last_use, is_deleted
FROM tokens;

-- Copy token_categories data
INSERT INTO token_categories_new (id, token_id, category_id, is_deleted)
SELECT id, CAST(token_id AS TEXT), CAST(category_id AS TEXT), is_deleted
FROM token_categories;

-- Copy urls data
INSERT INTO urls_new (id, hostname, description, bc_cats, is_deleted)
SELECT CAST(id AS TEXT), hostname, description, bc_cats, is_deleted
FROM urls;

-- Copy url_categories data
INSERT INTO url_categories_new (id, url_id, category_id, is_deleted)
SELECT id, CAST(url_id AS TEXT), CAST(category_id AS TEXT), is_deleted
FROM url_categories;

-- Step 3: Drop old tables
DROP TABLE url_categories;
DROP TABLE urls;
DROP TABLE token_categories;
DROP TABLE tokens;
DROP TABLE sub_category;
DROP TABLE categories;

-- Step 4: Rename new tables to original names
ALTER TABLE categories_new RENAME TO categories;
ALTER TABLE sub_category_new RENAME TO sub_category;
ALTER TABLE tokens_new RENAME TO tokens;
ALTER TABLE token_categories_new RENAME TO token_categories;
ALTER TABLE urls_new RENAME TO urls;
ALTER TABLE url_categories_new RENAME TO url_categories;

-- Step 5: Recreate indexes
CREATE UNIQUE INDEX IF NOT EXISTS unique_parent_child_deleted ON sub_category (parent_id, child_id, is_deleted);
CREATE UNIQUE INDEX IF NOT EXISTS unique_token_category_deleted ON token_categories (token_id, category_id, is_deleted);
CREATE UNIQUE INDEX IF NOT EXISTS unique_url_category_deleted ON url_categories (url_id, category_id, is_deleted);

-- Insert records to mark the migration
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Converted all ID columns from INTEGER to TEXT', 'system');
INSERT INTO history (time, description, user) VALUES (strftime('%s', 'now'), 'Migrated DB to version: 7', 'system');
