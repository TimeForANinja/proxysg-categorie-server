# Environment Variables Configuration

This document provides details about the environment variables available in this application.

You can, for example, provide them via a single `.env` file to fully configure the application.

## Summary Table

| Variable            | Var Level-2    | Var Level-3       | Default Value            | Description                                                                                  | Dependencies                     |
|---------------------|----------------|-------------------|--------------------------|----------------------------------------------------------------------------------------------|----------------------------------|
| `APP_DB`            | `__TYPE`       |                   | `sqlite`                 | Database type                                                                                | -                                |
| `APP_DB`            | `__SQLITE`     | `__FILENAME`      | `./data/mydatabase.db`   | SQLite database filepath                                                                     | Requires `APP_DB_TYPE=sqlite`    |
|                     |                |                   |                          |                                                                                              |                                  |
| `APP_PORT`          |                |                   | `8080`                   | Application port                                                                             | -                                |
| `APP_LOGLEVEL`      |                |                   | `INFO`                   | Set the CLI Loglevel of the App (e.g. INFO, DEBUG, ...)                                      | -                                |
| `APP_TIMEZONE`      |                |                   | `Europe/Berlin`          | Timezone (used for CRON)                                                                     | -                                |
| `APP_PROXY_FIX`     |                |                   | `false`                  | if 'true' the WSGI parses x-forwarded-for Headers                                            | -                                |
|                     |                |                   |                          |                                                                                              |                                  |
| `APP_SYSLOG`        | `__SERVER`     |                   | (empty => disabled)      | FQDN of the Syslog server                                                                    |                                  |
| `APP_SYSLOG`        | `__PORT`       |                   | 514                      | Port of the Syslog Server                                                                    |                                  |
|                     |                |                   |                          |                                                                                              |                                  |
| `APP_AUTH`          | `__ORDER`      |                   | `local`                  | Comma Separated List of Authentication type                                                  | -                                |
| `APP_AUTH`          | `__LOCAL`      | `__USER`          | `admin`                  | Local authentication username                                                                | Requires `APP_AUTH_ORDER=local`  |
| `APP_AUTH`          | `__LOCAL`      | `__PASSWORD`      | `nw_admin_2025`          | Local authentication password                                                                | Requires `APP_AUTH_ORDER=local`  |
|                     |                |                   |                          |                                                                                              |                                  |
| `APP_JWT`           | `__LIFETIME`   |                   | `21600` (6h)             | Lifetime of JWT Tokens in Seconds                                                            | -                                |
| `APP_JWT`           | `__SECRET`     |                   | -                        | Secret used for JWT Tokens                                                                   | -                                |
