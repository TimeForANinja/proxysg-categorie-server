import dataclasses
import json
import sys
from apiflask import APIFlask
import logging
from logging.handlers import SysLogHandler
from loguru import logger
from typing import Any


# Intercept handler to redirect logs to syslog
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
            logger.log(level, record.getMessage())
        except Exception as e:
            logger.warning(f"Failed to log via loguru: level={record.levelname}, err={e}")


def setup_logging(app: APIFlask):
    # remove all loggers
    logger.remove()

    # determine desired log level
    loglevel = str(app.config.get('LOGLEVEL', 'INFO')).upper()

    # use stdout as a default sink
    # - enqueue=True writes via a background thread (non-blocking)
    logger.add(sys.stdout, level=loglevel, enqueue=True)

    # Redirect stdlib logging into loguru
    # Keep the root logger at level=0 (ALL)
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # for some reason having pymongo on DEBUG or ALL breaks the app...
    logging.getLogger('pymongo').setLevel(logging.INFO)

    # if a syslog server is defined, also send it there
    syslog_server = app.config.get('SYSLOG', {}).get('SYSLOG_SERVER', None)
    if syslog_server is not None:
        syslog_port = int(app.config.get('SYSLOG', {}).get('SYSLOG_PORT', 514))
        handler = SysLogHandler(address=(syslog_server, syslog_port))
        logger.add(handler)


# custom JSON encoder to handle dataclasses and other objects that can't be serialized by default
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def _to_json(attachment: Any) -> str:
    # noinspection PyBroadException
    try:
        return json.dumps(attachment, cls=EnhancedJSONEncoder)
    except:
        return str(attachment)


def _remove_keys_from_json(json_str: str, *keys_to_remove: str) -> str:
    """Remove specified keys from a JSON string after serialization."""
    if not keys_to_remove:
        return json_str
    try:
        # Parse the JSON string
        data = json.loads(json_str)
        # Handle both single objects and lists/tuples
        if isinstance(data, (list, tuple)):
            for item in data:
                if isinstance(item, dict):
                    for key in keys_to_remove:
                        item.pop(key, None)
        elif isinstance(data, dict):
            for key in keys_to_remove:
                data.pop(key, None)
        # Convert back to JSON string
        return json.dumps(data)
    except:
        return json_str


def log_debug(module: str, message: str, *attachment: Any, exclude_keys: tuple[str, ...] = ()):
    serialized = _to_json(attachment)
    if exclude_keys:
        serialized = _remove_keys_from_json(serialized, *exclude_keys)
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).debug(f'{module} | {message} | {serialized}')

def log_error(module: str, message: str, *attachment: Any, exclude_keys: tuple[str, ...] = ()):
    serialized = _to_json(attachment)
    if exclude_keys:
        serialized = _remove_keys_from_json(serialized, *exclude_keys)
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).error(f'{module} | {message} | {serialized}')

def log_info(module: str, message: str, *attachment: Any, exclude_keys: tuple[str, ...] = ()):
    serialized = _to_json(attachment)
    if exclude_keys:
        serialized = _remove_keys_from_json(serialized, *exclude_keys)
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).info(f'{module} | {message} | {serialized}')
