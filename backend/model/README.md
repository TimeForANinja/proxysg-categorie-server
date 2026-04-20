# Model Module

This directory contains the core data models and business logic for the application, featuring a Git-inspired versioning system for managing categories, URLs, and tokens.

## Overview

The model layer acts as the bridge between the database abstraction and the REST API. It implements a content-addressable storage system where changes are tracked via commits and branches, allowing for staging changes and production releases.

### Key Components

- `model.py`: The entry point (`MyModel`) that initializes and coordinates all sub-models.
- `core.py`: Manages the versioning logic, including branches, commits, and the state tree root.
- `types/`: Defines the data structures (dataclasses) for all entities:
  - `core.py`: `Commit`, `Core`, and `StateTreeRootNode`.
  - `category.py`: `Category` definitions.
  - `url.py`: `URL` definitions.
  - `token.py`: `Token` definitions.
  - `mappings.py`: Relationships between URLs/Tokens and Categories.
- `category.py`, `url.py`, `token.py`, `mappings.py`: specialized models for CRUD operations on specific entities.
- `special.py`: Provides optimized read-only routes and complex data aggregation for the frontend.

## Versioning Architecture

The system uses a Git-like structure to manage data consistency and change tracking:

1. **Core**: A singleton object pointing to the current head of each branch.
2. **Branch**: A named pointer (e.g., `b_prod` for production, `b_user_<name>` for staging) to a specific commit.
3. **Commit**: An immutable snapshot containing metadata (author, timestamp, description) and a reference to a `StateTreeRootNode`.
4. **StateTreeRootNode**: A root node that holds lists of hashes for all objects (Categories, URLs, Tokens, and Mappings) at that point in time.

This architecture enables:
- **Atomic Commits**: Multiple changes can be grouped and published at once.
- **Staging**: Users work on their own branches without affecting production.
- **Diffing**: Efficiently calculating changes between any two points in history.

## Data Layout

The logical hierarchy of the data is as follows:

```text
Core
  └── Branches (e.g., b_prod, b_user_admin)
        └── Commit
              └── StateTreeRootNode
                    ├── Categories [ID, Name, ...]
                    ├── URLs [ID, Value, ...]
                    ├── Tokens [ID, Value, ...]
                    └── Mappings (Links URLs/Tokens to Categories)
```

## Usage

Most interactions happen through `MyModel`, which exposes sub-models:

```python
# Example: Fetching categories from the production branch
categories = model.specials.fetch_categories("b_prod")

# Example: Committing user changes to production
model.core.commit(user, "Updated blocked URLs")
```

## Configuration

The following configuration settings are used by the `model` module, particularly for BlueCoat (BC) category queries:

### BC Configuration Group

- `BC.HOST` (Required): The hostname or IP address of the BlueCoat Proxy.
- `BC.PASSWORD` (Required): The password for the BlueCoat Proxy management API.
- `BC.USER` (Default: `ro_admin`): The username for the BlueCoat Proxy management API.
- `BC.TIMEOUT` (Default: `10`): The HTTP timeout in seconds for requests to the BlueCoat Proxy.
- `BC.VERIFY_SSL` (Default: `true`): Whether to verify the SSL certificate of the BlueCoat Proxy.

These settings are typically loaded from environment variables during application initialization.
