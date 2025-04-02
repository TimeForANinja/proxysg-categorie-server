# Environment Variables Configuration

This document provides details about the environment variables available in this application.

You can for example provide them via a single `.env` file to fully configure the application.

## Summary Table

| Variable                    | Default Value          | Description                   | Dependencies                  |
|-----------------------------|------------------------|-------------------------------|-------------------------------|
| `APP_DB_TYPE`               | `sqlite`               | Database type                 | -                             |
| `APP_DB_SQLITE_FILENAME`    | `./Data/mydatabase.db` | SQLite database filepath      | Requires `APP_DB_TYPE=sqlite` |
| `APP_DB_MONGO_DBNAME`       | `proxysg_localdb`      | MongoDB database name         | Requires `APP_DB_TYPE=mongodb` |
| `APP_DB_MONGO_CON_USER`     | `admin`                | MongoDB username              | Requires `APP_DB_TYPE=mongodb` |
| `APP_DB_MONGO_CON_PASSWORD` | `adminpassword`        | MongoDB password              | Requires `APP_DB_TYPE=mongodb` |
| `APP_DB_MONGO_CON_HOST`     | `localhost:27017`      | MongoDB host and port         | Requires `APP_DB_TYPE=mongodb` |
|                             |                        |                               |                               |
| `APP_PORT`                  | `8080`                 | Application port              | -                             |
|                             |                        |                               |                               |
| `APP_AUTH_TYPE`             | `local`                | Authentication type           | -                             |
| `APP_AUTH_LOCAL_USER`       | `admin`                | Local authentication username | Requires `APP_AUTH_TYPE=local` |
| `APP_AUTH_LOCAL_PASSWORD`   | `nw_admin_2025`        | Local authentication password | Requires `APP_AUTH_TYPE=local` |
