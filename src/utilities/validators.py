"""Validators for the funtionalities of the app."""
import datetime
import re

import repackage

repackage.up()

from utilities.const import (
    DATE_FMT,
    DATE_LEN,
    DATE_RE,
    DATETIME_FMT,
    DATETIME_LEN,
    DATETIME_RE,
    MAX_LENGTH,
    MIN_LENGTH,
)


class Google:
    @staticmethod
    def is_valid_bucket_name(bucket_name: str) -> bool:
        """
        Validates whether bucket name follows Google restraints:
        https://cloud.google.com/storage/docs/buckets.

        Args:
            bucket_name (str): Bucket name.

        Returns:
            bool: True if bucket name follows Google restraints, False
            otherwise.
        """
        forbidden_pattern = r"^g[oO0]{2}g(le)?[a-z0-9_\-]*[a-z0-9]?$"
        if len(bucket_name) > MAX_LENGTH or len(bucket_name) < MIN_LENGTH:
            return False
        if re.fullmatch(forbidden_pattern, bucket_name):
            return False
        valid_pattern = r"^[a-z0-9][a-z0-9_\-]*[a-z0-9]$"
        return bool(re.fullmatch(valid_pattern, bucket_name))

    @staticmethod
    def is_valid_uri(uri: str) -> bool:
        """
        Validates if URI is a valid Google Storage URI.

        Args:
            uri (str): URI.

        Returns:
            bool: True if URI is a valid URI, False otherwise.
        """
        valid_pattern = r"gs://(.*?)/(.*)"
        if re.match(valid_pattern, uri) is not None:
            return True
        return False


class NewsHandlerValidator:
    def is_valid_string(var) -> bool:
        """
        Validates if input is a valid string.

        Args:
            var (_type_): Input variable.

        Returns:
            bool: True if input is a valid string, False otherwise.
        """
        return isinstance(var, str)

    def validate_date_str(datestr: str):
        """
        Checks if input is a valid `DATE_RE` representation.

        Args:
            datestr (str): Date string to validate.

        Raises:
            ValueError: If `datestr` is not a valid `DATE_RE` representation.
        """
        if not DATE_RE.match(datestr):
            raise ValueError("Date input should be in format of YYYY-MM-DD")

    def validate_datetime_str(datetimestr: str):
        """
        Checks if input is a valid `DATETIME_RE` representation.

        Args:
            datetimestr (str): Datetime string to validate.

        Raises:
            ValueError: If `datetimestr` is not a valid `DATETIME_RE` representation.
        """
        if not DATETIME_RE.match(datetimestr):
            raise ValueError("Datetime input should be in format of YYYY-MM-DDTHH:MM:SS")

    def is_valid_num(var) -> bool:
        """
        Validates if input is a valid number (int or float).

        Args:
            var (_type_): Input variable.

        Returns:
            bool: True if input is a valid number, False otherwise.
        """
        return isinstance(var, (int, float))


def stringify_date_param(dt):
    """Returns string representation of a date parameter"""
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
