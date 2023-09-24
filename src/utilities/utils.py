from __future__ import unicode_literals

import logging
import random
import sys
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

import coloredlogs
from google.cloud import storage


class CustomLogger:
    def __init__(self, name, mode="local"):
        self.logger = logging.getLogger(name)

        # Configure console logger with colored log levels
        console_handler = logging.StreamHandler(sys.stdout)
        # Create a custom formatter
        console_formatter = coloredlogs.ColoredFormatter(
            fmt="%(asctime)s : %(name)s : %(levelname)-10s : %(message)s",
            field_styles={
                "hostname": {"color": "white"},
                "programname": {"color": "white"},
                "name": {"color": "white"},
                "levelname": {"color": "white"},
                "asctime": {"color": "white"},
            },
            level_styles={
                "debug": {"color": "cyan", "bold": True},
                "info": {"color": "green", "bold": True},
                "warning": {"color": "yellow", "bold": True},
                "error": {"color": "red", "bold": True},
                "critical": {"color": "red", "bold": True},
            },
        )

        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Configure local file logger for warnings and above
        local_file_handler = RotatingFileHandler(
            "example.log", maxBytes=100000, backupCount=1
        )
        local_file_handler.setLevel(logging.WARNING)
        # Create a custom formatter
        local_file_formatter = logging.Formatter(
            fmt="%(asctime)s : %(name)s : %(levelname)s : %(message)s"
        )
        local_file_handler.setFormatter(local_file_formatter)
        self.logger.addHandler(local_file_handler)

        if mode == "gcp":
            # Configure Google Cloud Storage logger for errors and above
            gcs_handler = GCSHandler("example.log", "your-google-cloud-bucket-name")
            gcs_handler.setLevel(logging.WARNING)
            # Create a custom formatter
            gcs_formatter = logging.Formatter(
                fmt="%(asctime)s : %(name)s : %(levelname)s : %(message)s"
            )
            gcs_handler.setFormatter(gcs_formatter)
            self.logger.addHandler(gcs_handler)

        # Set the minimum log level for the logger
        self.logger.setLevel(logging.DEBUG)

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


class GCSHandler(logging.StreamHandler):
    def __init__(self, filename, bucket_name):
        super().__init__()
        self.filename = filename
        self.bucket_name = bucket_name
        self.client = storage.Client()

    def emit(self, record):
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blob = bucket.blob(self.filename)
            blob.upload_from_string(self.format(record) + "\n", content_type="text/plain")
        except Exception as e:
            print(f"Error uploading log to Google Cloud Storage: {e}")


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
