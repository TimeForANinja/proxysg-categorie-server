import json
import apiflask
import logging
from logging.handlers import SysLogHandler
from loguru import logger


# Intercept handler to redirect logs to syslog
class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        logger.log(level, record.getMessage())


def setup_logging(app: apiflask):
    # redirect all logs to our custom log handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # if a syslog server is defined also send it there
    # TODO: replace other os.getenv with app.config
    syslog_server = app.config.get('SYSLOG_SERVER', None)
    if syslog_server is not None:
        syslog_port = int(app.config.get('SYSLOG_PORT', 514))
        handler = SysLogHandler(address=(syslog_server, syslog_port))
        logger.add(handler)


def log_debug(module: str, message: str, *attachment: any):
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).debug(f"{module}: {message} -- {json.dumps(attachment)}")

def log_error(module: str, message: str, *attachment: any):
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).error(f"{module}: {message} -- {json.dumps(attachment)}")

def log_info(module: str, message: str, *attachment: any):
    # depth=1 is set so that we log the position log_debug was called and not logger.debug
    logger.opt(depth=1).info(f"{module}: {message} -- {json.dumps(attachment)}")
