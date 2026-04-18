# Authentication Module

This directory contains the authentication logic for the application, designed to be extensible via a provider-based architecture.

## Overview

The authentication system is built around `APIFlask` and uses JWT (JSON Web Tokens) for session management. It supports multiple authentication "realms" (providers) that can be prioritized via configuration.

### Key Files

- `auth.py`: Defines the `AuthHandler`, which coordinates multiple auth realms and integrates with APIFlask's `HTTPTokenAuth`.
- `auth_realm.py`: Contains the `AuthRealmInterface` that every auth provider must implement, and the `AuthProviderInterface` for the provider's Plugin API.
- `auth_user.py`: Defines the `AuthUser` dataclass, representing an authenticated user and their roles.
- `auth_singleton.py`: Handles dynamic discovery and initialization of auth providers based on application configuration.
- `jwt/`: Contains JWT handling logic (`jwt_handler.py`, `jwt_data.py`).

## Adding a New Provider

Adding a new authentication provider is simple and follows a pattern similar to the `static` provider.

1. **Create a subfolder** in `auth/` (e.g., `auth/ldap/`).
2. **Implement the provider logic** in a file ending with `_auth.py` (e.g., `auth/ldap/ldap_auth.py`).
3. **Expose the Plugin API**: The module must define a class named `AuthProvider` that inherits from `AuthProviderInterface`:
    - `auth_fits(self, app: APIFlask, auth_type: str) -> bool`: Returns `True` if this provider should handle the given `auth_type`. The `auth_type` is already normalized (stripped and lowercase).
    - `build_auth_realm(self, app: APIFlask, jwt: JWTHandler) -> AuthRealmInterface`: Factory function to instantiate the provider's realm implementation.
4. **Implement `AuthRealmInterface`**: Your provider must have a class that inherits from `AuthRealmInterface` and implements:
    - `check_login(username, password)`: To validate credentials and return a token + `AuthUser`.
    - `verify_token(token)`: To validate an existing JWT and return an `AuthUser`.

### Example Structure

```
auth/
└── my_provider/
    └── my_provider_auth.py  <-- Must end in _auth.py
```

### Configuration

Authentication is configured via environment variables (or `app.config`).

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH__ORDER` | `local` | Comma-separated list of auth providers (realms) in priority order. |
| `JWT__SECRET` | (required) | Secret key for JWT signing. |
| `JWT__LIFETIME` | `21600` | JWT token lifetime in seconds (default: 6 hours). |
| `AUTH__LOCAL__USER` | `admin` | Username for the static (`local`) auth provider. |
| `AUTH__LOCAL__PASSWORD` | `nw_admin_2025` | Password for the static (`local`) auth provider. |

To enable your new provider, add its identifier (the one matched by `auth_fits`) to the `AUTH__ORDER` configuration.
