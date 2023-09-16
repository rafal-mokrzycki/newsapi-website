"""Validators for the funtionalities of the app."""
import re

import repackage

repackage.up()

from utils.const import DATE_RE, DATETIME_RE, MAX_LENGTH, MIN_LENGTH


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
        Validates if URI is a valid URI.

        Args:
            uri (str): URI.

        Returns:
            bool: True if URI is a valid URI, Fals otherwise.
        """
        valid_pattern = r"gs://(.*?)/(.*)"
        if re.match(valid_pattern, uri) is not None:
            return True
        return False


class NewsHandlerValidator:
    def is_valid_string(var):
        return isinstance(var, str)

    def validate_date_str(datestr):
        if not DATE_RE.match(datestr):
            raise ValueError("Date input should be in format of YYYY-MM-DD")

    def validate_datetime_str(datetimestr):
        if not DATETIME_RE.match(datetimestr):
            raise ValueError("Datetime input should be in format of YYYY-MM-DDTHH:MM:SS")

    def is_valid_num(var):
        return isinstance(var, (int, float))
