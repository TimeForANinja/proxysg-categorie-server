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
    color INTEGER NOT NULL
);

-- Create urls table
CREATE TABLE IF NOT EXISTS urls (
    id TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    description TEXT NOT NULL,
    categories TEXT
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
