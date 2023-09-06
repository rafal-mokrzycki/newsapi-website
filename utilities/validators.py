"""Validators for the funtionalities of the app."""
import re


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
        MAX_LENGTH = 63
        MIN_LENGTH = 3
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
