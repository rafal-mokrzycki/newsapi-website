from __future__ import unicode_literals

import datetime
import logging
import random
import time
from functools import wraps

import repackage

repackage.up()
from utils.const import DATE_FMT, DATE_LEN, DATETIME_FMT, DATETIME_LEN
from utils.validators import NewsHandlerValidator

__all__ = ("stringify_date_param",)


def stringify_date_param(dt):
    if NewsHandlerValidator.is_valid_string(dt):
        if len(dt) == DATE_LEN:
            NewsHandlerValidator.validate_date_str(dt)
        elif len(dt) == DATETIME_LEN:
            NewsHandlerValidator.validate_datetime_str(dt)
        else:
            raise ValueError(
                "Date input should be in format of either YYYY-MM-DD \
                    or YYYY-MM-DDTHH:MM:SS"
            )
        return dt
    # Careful: datetime.datetime is subclass of datetime.date!
    elif isinstance(dt, datetime.datetime):
        # TODO: time zone
        return dt.strftime(DATETIME_FMT)
    elif isinstance(dt, datetime.date):
        return dt.strftime(DATE_FMT)
    elif NewsHandlerValidator.is_valid_num(dt):
        return datetime.datetime.utcfromtimestamp(dt).strftime(DATETIME_FMT)
    else:
        raise TypeError(
            "Date input must be one of: str, date, datetime, float, int, or None"
        )


class CustomLogger:
    # TODO: get rid of double logging

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create a custom formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s   %(message)s",
        )

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        self.logger.addHandler(console_handler)

        # Define custom log levels and colors
        logging.addLevelName(
            logging.DEBUG, "\033[36m%s\033[0m" % logging.getLevelName(logging.DEBUG)
        )
        logging.addLevelName(
            logging.INFO, "\033[37m%s\033[0m" % logging.getLevelName(logging.INFO)
        )
        logging.addLevelName(
            logging.WARNING, "\033[33m%s\033[0m" % logging.getLevelName(logging.WARNING)
        )
        logging.addLevelName(
            logging.ERROR, "\033[31m%s\033[0m" % logging.getLevelName(logging.ERROR)
        )
        logging.addLevelName(
            logging.CRITICAL, "\033[31m%s\033[0m" % logging.getLevelName(logging.CRITICAL)
        )

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time() - t1
        logging.info(f"`{func.__name__}` ran in {t2} seconds")
        return result

    return wrapper


def wait_for_web_scraping():
    time.sleep(random.randint(5, 10))
