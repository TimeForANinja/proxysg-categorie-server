# Environment Variables Configuration

This document provides details about the environment variables available in this application.

You can for example provide them via a single `.env` file to fully configure the application.

## Summary Table

| Variable                    | Default Value            | Description                                                                     | Dependencies                     |
|-----------------------------|--------------------------|---------------------------------------------------------------------------------|----------------------------------|
| `APP_DB_TYPE`               | `sqlite`                 | Database type                                                                   | -                                |
| `APP_DB_SQLITE_FILENAME`    | `./data/mydatabase.db`   | SQLite database filepath                                                        | Requires `APP_DB_TYPE=sqlite`    |
| `APP_DB_MONGO_DBNAME`       | `proxysg_localdb`        | MongoDB database name                                                           | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB_MONGO_CON_USER`     | `admin`                  | MongoDB username                                                                | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB_MONGO_CON_PASSWORD` | `adminpassword`          | MongoDB password                                                                | Requires `APP_DB_TYPE=mongodb`   |
| `APP_DB_MONGO_CON_HOST`     | `localhost:27017`        | MongoDB host and port                                                           | Requires `APP_DB_TYPE=mongodb`   |
|                             |                          |                                                                                 |                                  |
| `APP_PORT`                  | `8080`                   | Application port                                                                | -                                |
|                             |                          |                                                                                 |                                  |
| `APP_AUTH_ORDER`            | `local`                  | Comma Separated List of Authentication type                                     | -                                |
| `APP_AUTH_LOCAL_USER`       | `admin`                  | Local authentication username                                                   | Requires `APP_AUTH_ORDER=local`  |
| `APP_AUTH_LOCAL_PASSWORD`   | `nw_admin_2025`          | Local authentication password                                                   | Requires `APP_AUTH_ORDER=local`  |
| `APP_AUTH_RADIUS_SERVER`    | -                        | Radius Auth Server IP / Hostname                                                | Requires `APP_AUTH_ORDER=radius` |
| `APP_AUTH_RADIUS_SECRET`    | -                        | Pre-Shared-Secret to use for Radius                                             | Requires `APP_AUTH_ORDER=radius` |
|                             |                          |                                                                                 |                                  |
| `APP_JWT_LIFETIME`          | -                        | Lifetime of JWT Tokens in Seconds                                               | -                                |
| `APP_JWT_SECRET`            | -                        | Secret used for JWT Tokens                                                      | -                                |
|                             |                          |                                                                                 |                                  |
| `APP_BC_DB`                 |                          | fqdn or ip of the BC proxy                                                      | -                                |
| `APP_BC_INTERVAL`           | `0 3 * * *` (daily, 3am) | interval at which to update BC cats (full). "Cron"-Format                       | Requires `APP_BC_DB`             |
| `APP_BC_INTERVAL_QUICK`     | `0 * * * *` (hourly)     | interval at which to update BC cats (only not yet categorised). "Cron"- Formmat | Requires `APP_BC_DB`             |
| `APP_BC_USER`               | `ro_admin`               | username to query the proxy                                                     | Requires `APP_BC_DB`             |
| `APP_BC_PASSWORD`           | -                        | password to query the proxy                                                     | Requires `APP_BC_DB`             |
| `APP_BC_VERIFY_SSL`         | `true`                   | verify the proxy https certificate? (true / false)                              | Requires `APP_BC_DB`             |
|                             |                          |                                                                                 |                                  |
| `APP_LOAD_EXISTING_PATH`    | `./data/local_db.txt`    | Path to an existing DB (if any) to load                                         | -                                |
| `APP_LOAD_EXISTING_PREFIX`  | (empty string)           | Prefix for Cats of the imported LocalDB                                         | -                                |
