# SQLite Database Migration System

This folder contains migration scripts for the SQLite database. The migration system automatically applies new migrations when the application starts.

## How It Works

1. The system maintains a `schema-version` parameter in the `config` table to track the current database schema version.
2. On application startup, it checks for migration scripts in this folder.
3. It runs any migration scripts with a version number higher than the current schema version, in ascending order.
4. After each successful migration, it updates the schema version.

## Creating Migration Scripts

Migration scripts should follow these guidelines:

1. **Naming Convention**: Name your migration scripts in the format `<version>_<description>.sql`, where:
   - `<version>` is an integer that determines the order of execution (e.g., 1, 2, 3)
   - `<description>` is a brief description of what the migration does

   Example: `1_initial_schema.sql`, `2_add_user_table.sql`

2. **Content**: Each script should contain valid SQL statements that modify the database schema.

3. **Idempotency**: Migrations should be idempotent when possible (i.e., they can be run multiple times without causing errors).
   - Use `CREATE TABLE IF NOT EXISTS` instead of `CREATE TABLE`
   - Use `ALTER TABLE ... ADD COLUMN ... IF NOT EXISTS` if your SQLite version supports it

4. **Transactions**: The migration system automatically wraps each migration in a transaction, so you don't need to include `BEGIN TRANSACTION` and `COMMIT` statements.

## Example Migration Script

```sql
-- Migration script: 3_add_user_preferences.sql
-- Add user preferences table

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY,
    theme TEXT DEFAULT 'light',
    notifications BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add default preferences for existing users
INSERT INTO user_preferences (user_id)
SELECT id FROM users WHERE id NOT IN (SELECT user_id FROM user_preferences);

-- Record this migration in the history table
-- Note: Always include this at the end of your migration script
INSERT INTO history (time, description, user, ref_token, ref_url, ref_category) 
VALUES (strftime('%s', 'now'), 'Migrated DB to version: 3', 'system', '', '', '');
```

> **Important**: Always include a history record at the end of each migration script to document the version change.

## Troubleshooting

If a migration fails, the system will:
1. Roll back the transaction for that migration
2. Log an error message
3. Stop processing further migrations

To resolve migration issues:
1. Fix the error in the migration script
2. Restart the application to retry the migration
