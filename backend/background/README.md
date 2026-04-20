# Background Tasks Module

This directory contains the background scheduler and periodic tasks for the application. It uses `APScheduler` to manage long-running operations.

## Overview

The main entry point is `background_tasks.py`, which initializes the `BackgroundScheduler` and schedules all periodic jobs.

### Current Tasks

- **BlueCoat Category Refresh**: Periodically queries a BlueCoat Proxy for the current ratings of all URLs in the production branch. This ensures that the categorization remains up-to-date even for URLs that haven't been modified manually.

## Configuration

The background tasks are configured via environment variables and the Flask application configuration.

### Environment Variables / Config

The following settings are used under the `BC` configuration group:

- `BC.HOST` (Required): The hostname or IP address of the BlueCoat Proxy.
- `BC.PASSWORD` (Required): The password for the BlueCoat Proxy management API.
- `BC.USER` (Default: `ro_admin`): The username for the BlueCoat Proxy management API.
- `BC.INTERVAL` (Default: `0 3 * * *`): A cron expression defining when the full background refresh should run.
- `BC.TTL` (Default: `10080`): The Time-To-Live in minutes for cached categories. If a rating is older than this, it will be refreshed during the next cycle. Default is 7 days.
- `BC.TIMEOUT` (Default: `10`): The HTTP timeout in seconds for requests to the BlueCoat Proxy.
- `BC.VERIFY_SSL` (Default: `true`): Whether to verify the SSL certificate of the BlueCoat Proxy.

Global settings:

- `TIMEZONE` (Default: `Europe/Berlin`): The timezone used for all cron-based schedules.

## Execution Flow

1. **Startup**: On application start, `start_background_tasks(app)` is called.
2. **Initial Delay**: The first execution of the BC query is delayed by 5 minutes to allow the main application to fully initialize.
3. **Periodic Execution**: After the initial run, the task is scheduled according to the `BC.INTERVAL` cron expression.
4. **App Context**: Tasks run within a Flask `app_context` to ensure they have access to the database and configuration singletons.
