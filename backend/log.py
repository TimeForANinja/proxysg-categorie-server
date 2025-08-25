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
        level = logger.level(record.levelname).name
        logger.log(level, record.getMessage())


def setup_logging(app: APIFlask):
    # remove all loggers
    logger.remove()
    # add default stderr but allow for custom level
    loglevel = app.config.get('LOGLEVEL', 'INFO')
    logger.add(sys.stderr, level=loglevel)

    # redirect all logs to our custom log handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

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


def log_debug(module: str, message: str, *attachment: Any):
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).debug(f'{module} | {message} | {_to_json(attachment)}')

def log_error(module: str, message: str, *attachment: Any):
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).error(f'{module} | {message} | {_to_json(attachment)}')

def log_info(module: str, message: str, *attachment: Any):
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).info(f'{module} | {message} | {_to_json(attachment)}')
