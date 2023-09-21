from __future__ import unicode_literals

import logging
import random
import time
from functools import wraps


class CustomLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Create a custom formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s : %(name)s : %(levelname)s : %(message)s",
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
    """Wrapper for execution tim measurement"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time() - t1
        logging.info(f"`{func.__name__}` ran in {t2} seconds")
        return result

    return wrapper


def wait_for_web_scraping():
    """Wait so that program is not blocked be a scraped server"""
    time.sleep(random.randint(5, 10))
