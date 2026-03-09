-- Initial database schema creation (squashed)

-- Create a config table to track schema version
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Create a category table
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    color INTEGER NOT NULL,
    is_deleted INTEGER DEFAULT 0
);

-- Create a sub_category table
CREATE TABLE IF NOT EXISTS sub_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id TEXT,
    child_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    FOREIGN KEY (child_id) REFERENCES categories(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS unique_parent_child_deleted ON sub_category (parent_id, child_id, is_deleted);

-- Create a token table
CREATE TABLE IF NOT EXISTS tokens (
    id TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    description TEXT NOT NULL,
    last_use INTEGER DEFAULT 0,
    is_deleted INTEGER DEFAULT 0
);

-- Create token_categories table
CREATE TABLE IF NOT EXISTS token_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id TEXT,
    category_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (token_id) REFERENCES tokens(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS unique_token_category_deleted ON token_categories (token_id, category_id, is_deleted);

-- Create urls table
CREATE TABLE IF NOT EXISTS urls (
    id TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    description TEXT NOT NULL,
    bc_cats TEXT NOT NULL,
    bc_last_set INTEGER DEFAULT 0,
    is_deleted INTEGER DEFAULT 0
);

-- Create url_categories table
CREATE TABLE IF NOT EXISTS url_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id TEXT,
    category_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (url_id) REFERENCES urls(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS unique_url_category_deleted ON url_categories (url_id, category_id, is_deleted);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user TEXT NOT NULL,
    parameters TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Create Tags table
CREATE TABLE IF NOT EXISTS tags (
    label TEXT PRIMARY KEY,
    hash TEXT NOT NULL
);

-- Create Sets table
CREATE TABLE IF NOT EXISTS sets (
    uuid TEXT NOT NULL,
    type TEXT NOT NULL,
    entries TEXT NOT NULL,
    PRIMARY KEY (uuid, type)
);
-- Record the schema version in the config table
INSERT OR REPLACE INTO config (key, value) VALUES ('schema-version', '1');
