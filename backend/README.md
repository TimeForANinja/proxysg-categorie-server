# Environment Variables Configuration

This document provides details about the environment variables available in this application.

You can, for example, provide them via a single `.env` file to fully configure the application.

## Summary Table

| Variable            | Var Level-2        | Var Level-3       | Default Value            | Description                                                                                  | Dependencies                     |
|---------------------|--------------------|-------------------|--------------------------|----------------------------------------------------------------------------------------------|----------------------------------|
| `APP_DB`            | `__TYPE`           |                   | `sqlite`                 | Database type                                                                                | -                                |
| `APP_DB`            | `__SQLITE`         | `__FILENAME`      | `./data/mydatabase.db`   | SQLite database filepath                                                                     | Requires `APP_DB_TYPE=sqlite`    |
| `APP_DB`            | `__MONGO`          | `__DBNAME`        | `proxysg_localdb`        | MongoDB database name                                                                        | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB`            | `__MONGO`          | `__DBAUTH`        | <defaults to __DBNAME>   | MongoDB Database to use for Authentication                                                   | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB`            | `__MONGO`          | `__CON_USER`      | `admin`                  | MongoDB username                                                                             | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB`            | `__MONGO`          | `__CON_PASSWORD`  | `adminpassword`          | MongoDB password                                                                             | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB`            | `__MONGO`          | `__CON_HOST`      | `localhost`              | MongoDB hostname or ip                                                                       | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB`            | `__MONGO`          | `__CON_PORT`      | `27017`                  | MongoDB server port                                                                          | Requires `APP_DB_TYPE=mongodb`   |
|                     |                    |                   |                          |                                                                                              |                                  |
| `APP_PORT`          |                    |                   | `8080`                   | Application port                                                                             | -                                |
| `APP_LOGLEVEL`      |                    |                   | `INFO`                   | Set the CLI Loglevel of the App (e.g. INFO, DEBUG, ...)                                      | -                                |
| `APP_TIMEZONE`      |                    |                   | `Europe/Berlin`          | Timezone (used for CRON)                                                                     | -                                |
| `APP_PROXY_FIX`     |                    |                   | `false`                  | if 'true' the WSGI parses x-forwarded-for Headers                                            | -                                |
|                     |                    |                   |                          |                                                                                              |                                  |
| `APP_SYSLOG`        | `__SERVER`         |                   | (empty => disabled)      | FQDN of the Syslog server                                                                    |                                  |
| `APP_SYSLOG`        | `__PORT`           |                   | 514                      | Port of the Syslog Server                                                                    |                                  |
|                     |                    |                   |                          |                                                                                              |                                  |
| `APP_AUTH`          | `__ORDER`          |                   | `local`                  | Comma Separated List of Authentication type                                                  | -                                |
| `APP_AUTH`          | `__LOCAL`          | `__USER`          | `admin`                  | Local authentication username                                                                | Requires `APP_AUTH_ORDER=local`  |
| `APP_AUTH`          | `__LOCAL`          | `__PASSWORD`      | `nw_admin_2025`          | Local authentication password                                                                | Requires `APP_AUTH_ORDER=local`  |
| `APP_AUTH`          | `__RADIUS`         | `__SERVER`        | -                        | Radius Auth Server IP / Hostname                                                             | Requires `APP_AUTH_ORDER=radius` |
| `APP_AUTH`          | `__RADIUS`         | `__SECRET`        | -                        | Pre-Shared-Secret to use for Radius                                                          | Requires `APP_AUTH_ORDER=radius` |
| `APP_AUTH`          | `__RADIUS`         | `__ROLE_MAP`      | (empty => no mapping)    | A "Map" to translate Groups from the Radius API to internal Rules (see Role Map for Details) | Requires `APP_AUTH_ORDER=radius` |
| `APP_AUTH`          | `__REST`           | `__AUTH_URL`      | -                        | URL for an API Endpoint that resolves a body of user&password to a user profile and token    | Requires `APP_AUTH_ORDER=rest`   |
| `APP_AUTH`          | `__REST`           | `__VERIFY_URL`    | -                        | URL for an API Endpoint for resolving a token to a user                                      | Requires `APP_AUTH_ORDER=rest`   |
| `APP_AUTH`          | `__REST`           | `__SSL_VERIFY`    | `true`                   | verify the API Endpoints https certificate? (true / false)                                   | Requires `APP_AUTH_ORDER=rest`   |
| `APP_AUTH`          | `__REST`           | `__PATH_USERNAME` | `username`               | Path in the response JSON of the API Endpoint that includes the username                     | Requires `APP_AUTH_ORDER=rest`   |
| `APP_AUTH`          | `__REST`           | `__PATH_GROUPS`   | `groups`                 | Path in the response JSON of the API Endpoint that includes the string list of groups        | Requires `APP_AUTH_ORDER=rest`   |
| `APP_AUTH`          | `__REST`           | `__PATH_TOKEN`    | `token`                  | Path in the response JSON of the API Endpoint that includes the token for future requests    | Requires `APP_AUTH_ORDER=rest`   |
| `APP_AUTH`          | `__REST`           | `__ROLE_MAP`      | (empty => no mapping)    | A "Map" to translate Groups from the Radius API to internal Rules (see Role Map for Details) | Requires `APP_AUTH_ORDER=rest`   |
|                     |                    |                   |                          |                                                                                              |                                  |
| `APP_JWT`           | `__LIFETIME`       |                   | `21600` (6h)             | Lifetime of JWT Tokens in Seconds                                                            | -                                |
| `APP_JWT`           | `__SECRET`         |                   | -                        | Secret used for JWT Tokens                                                                   | -                                |
|                     |                    |                   |                          |                                                                                              |
| `APP_BC`            | `__HOST`           |                   |                          | fqdn or ip of the BC proxy                                                                   | -                                |
| `APP_BC`            | `__INTERVAL`       |                   | `0 3 * * *` (daily, 3am) | interval at which to update BC cats (full). 'Cron'-Format                                    | Requires `APP_BC_DB`             |
| `APP_BC`            | `__INTERVAL_QUICK` |                   | `0 * * * *` (hourly)     | interval at which to update BC cats (only not yet categorised). 'Cron'- Format               | Requires `APP_BC_DB`             |
| `APP_BC`            | `__USER`           |                   | `ro_admin`               | username to query the proxy                                                                  | Requires `APP_BC_DB`             |
| `APP_BC`            | `__PASSWORD`       |                   | -                        | password to query the proxy                                                                  | Requires `APP_BC_DB`             |
| `APP_BC`            | `__VERIFY_SSL`     |                   | `true`                   | verify the proxy https certificate? (true / false)                                           | Requires `APP_BC_DB`             |
|                     |                    |                   |                          |                                                                                              |                                  |
| `APP_LOAD_EXISTING` | `__PATH`           |                   | `./data/local_db.txt`    | Path to an existing DB (if any) to load                                                      | -                                |
| `APP_LOAD_EXISTING` | `__PREFIX`         |                   | (empty string)           | Prefix for Cats of the imported LocalDB                                                      | -                                |

### Role Map

A Role Map allows for Mapping Group Memberships from an external authentication provider (like RADIUS or REST) to the internal Roles.
The mapping is specified as a comma-separated list of role assignments.

#### Syntax

```
map = "" | <mapping> | <mapping> "," <map>

mapping = <external_role> "=" <internal_role>
internal_role = "ro" | "rw"
```

#### Examples
The below table shows a few examples.
The "Example" Columns indicate how a User with the row "external_ro" or "external_unknown" would behave
`INTERNAL_RW` / `INTERNAL_RO` is a placeholder for the use-case were you named a Role identical to how we handle them internally.

| Role Map                      | Description                                  | Role before Mapping | Role after Mapping |
|-------------------------------|----------------------------------------------|---------------------|--------------------|
| external_ro=ro                | Simple single mapping                        | "external_rw"       | "external_rw"      |
|                               |                                              | "external_ro"       | "INTERNAL_RO"      |
|                               |                                              | "external_unknown"  | "external_unknown" |
|                               |                                              | "INTERNAL_RW"       | "INTERNAL_RW"      |
|                               |                                              |                     |                    |
| external_ro=ro,external_rw=rw | Map multiple roles                           | "external_rw"       | "INTERNAL_RW"      |
|                               |                                              | "external_ro"       | "INTERNAL_RO"      |
|                               |                                              | "external_unknown"  | "external_unknown" |
|                               |                                              | "INTERNAL_RW"       | "INTERNAL_RW"      |
|                               |                                              |                     |                    |
| \<empty\>                     | Defaults to keeping all Roles identical      | "external_rw"       | "external_rw"      |
|                               |                                              | "external_ro"       | "external_ro"      |
|                               |                                              | "external_unknown"  | "external_unknown" |
|                               |                                              | "INTERNAL_RW"       | "INTERNAL_RW"      |
|                               |                                              |                     |                    |
| INTERNAL_RW=ro                | Overwrite mapping for similarly named groups | "external_rw"       | "external_rw"      |
|                               |                                              | "external_ro"       | "external_ro"      |
|                               |                                              | "external_unknown"  | "external_unknown" |
|                               |                                              | "INTERNAL_RW"       | "INTERNAL_RO"      |


#### Notes
- If no mapping is defined for a user's group, the original group name is used as-is
- only the "external_role" part of the mapping is case-sensitive
