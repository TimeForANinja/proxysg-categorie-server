-- Migration script: 1_initial_schema.sql
-- Initial database schema creation

-- Create config table
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    color INTEGER NOT NULL,
    is_deleted INTEGER DEFAULT 0
);

-- Create sub_category table
CREATE TABLE IF NOT EXISTS sub_category (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    child_id INTEGER,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    FOREIGN KEY (child_id) REFERENCES categories(id)
);

-- Create history table
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY,
    time INTEGER NOT NULL,
    description TEXT
);

-- Create tokens table
CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY,
    token TEXT NOT NULL,
    description TEXT NOT NULL,
    last_use INTEGER DEFAULT 0,
    is_deleted INTEGER DEFAULT 0
);

-- Create token_categories table
CREATE TABLE IF NOT EXISTS token_categories (
    id INTEGER PRIMARY KEY,
    token_id INTEGER,
    category_id INTEGER,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (token_id) REFERENCES tokens(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Create urls table
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    hostname TEXT NOT NULL,
    description TEXT NOT NULL,
    bc_cats TEXT NOT NULL,
    is_deleted INTEGER DEFAULT 0
);

-- Create url_categories table
CREATE TABLE IF NOT EXISTS url_categories (
    id INTEGER PRIMARY KEY,
    url_id INTEGER,
    category_id INTEGER,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (url_id) REFERENCES urls(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Insert initial values
INSERT INTO history (time, description) VALUES (strftime('%s', 'now'), 'Database created');
