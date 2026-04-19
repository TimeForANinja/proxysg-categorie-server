# Database Module

This directory contains the database abstraction layer and various storage backends.

## Overview

The database system is built around a common interface (`DBInterface`) which allows the application to switch between different storage technologies (DBM, MongoDB, SQLite) without changing the core business logic.

### Key Components

- `abc/`: Contains the `DBInterface` (the contract for all backends) and global constants.
- `db_singleton.py`: The central factory for obtaining a database instance, handling initialization and backend selection based on configuration.
- `cache/`: A middleware layer that provides in-memory caching (LFU) for any `DBInterface` implementation.
- `dbm/`: A simple, file-based key-value backend using the Python `dbm` module.
- `mongo/`: A backend implementation for MongoDB, suitable for scalable and distributed setups.
- `sqlite/`: A robust, single-file relational database backend using SQLite.
- `util/`: Helper utilities for hashing (SHA256) and data serialization (BSON).

## Architecture

The system uses a layered approach:
1. **Model Layer**: `MyModel` interacts with the `DBInterface`.
2. **Middleware Layer**: (Optional) `CacheDB` intercepts reads to improve performance.
3. **Backend Layer**: The actual storage implementation (SQLite, Mongo, or DBM).

### Sharding Large Lists

To handle large lists of IDs efficiently and avoid storage limits in some backends, the system automatically shards lists into smaller subsets. This is transparently handled by the `insert_id_list` and `fetch_id_list` methods in each backend.

## Configuration

The database system is configured via environment variables (or `app.config`).

### Environment Variables

| Variable                    | Default                    | Description                                                             |
|-----------------------------|----------------------------|-------------------------------------------------------------------------|
| `DB__TYPE`                  | (required)                 | Type of backend: `dbm`, `mongo`, or `sqlite`.                           |
| `DB__CACHE_DISABLED`        | `false`                    | Set to `true` to disable the LFU caching layer.                         |
| `DB__DBM__FILENAME`         | `./data/mydatabase.dbm`    | File path for the DBM backend.                                          |
| `DB__MONGO__HOST`           | `localhost`                | MongoDB server hostname.                                                |
| `DB__MONGO__PORT`           | `27017`                    | MongoDB server port.                                                    |
| `DB__MONGO__DATABASE`       | `proxysg`                  | MongoDB database name.                                                  |
| `DB__MONGO__USERNAME`       | (optional)                 | Username for MongoDB authentication.                                    |
| `DB__MONGO__PASSWORD`       | (optional)                 | Password for MongoDB authentication.                                    |
| `DB__MONGO__AUTHSOURCE`     | (database)                 | Database to authenticate against (defaults to `DB__MONGO__DATABASE`).   |
| `DB__MONGO__CONNECT_DIRECT` | `false`                    | Whether to connect directly to the host (bypass replica set discovery). |
| `DB__MONGO__COLLECTION`     | `data`                     | MongoDB collection name.                                                |
| `DB__SQLITE__FILENAME`      | `./data/mydatabase.sqlite` | File path for the SQLite backend.                                       |

### Backend Specifics

- `dbm`: Simple file-based storage.
- `mongo`: Scalable, document-oriented storage.
- `sqlite`: Robust, relational file-based storage.
