#!/usr/bin/env python3
import logging
import re
from pathlib import Path

from google.cloud import exceptions, storage

from config.config import load_config
from utilities.validators import Google

config = load_config()
log = logging.getLogger(__name__)


class GCP_Handler:
    def _init__(
        self,
        key_path: Path | None = None,
    ) -> None:
        if key_path is None:
            self.key_path = config["key_path"]
        else:
            self.key_path = key_path
        self.storage_client = storage.Client.from_service_account_json(self.key_path)
        self.project_name = config["project_name"]
        self.location = config["location"]

    def create_bucket(
        self,
        bucket_name: str,
        storage_class: str = "STANDARD",
        location: str | None = None,
    ) -> None:
        """
        Creates a new bucket.

        Args:
            bucket_name (str): new bucket name.
            storage_class (str): storage class.
            location (str | None): bucket location. If None - taken from the config.json.
            Defaults to None.
        """
        if location is None:
            location = self.location
        if Google.is_valid_bucket_name(bucket_name):
            try:
                bucket = self.storage_client.bucket(bucket_name)
                bucket.storage_class = storage_class
                self.storage_client.create_bucket(bucket_name, location=location)
                log.info("Bucket {} created".format(bucket_name))
            except (BaseException, exceptions.Conflict):
                # If the bucket already exists, ignore the 409 HTTP error and
                # continue with the rest of the program.
                log.warning("Bucket {} already exists.".format(bucket_name))
        else:
            raise NameError(
                f"Bucket name '{bucket_name}' does not follow Google \
                    requirements, \
                    see: https://cloud.google.com/storage/docs/buckets#naming"
            )

    def delete_bucket(self, bucket_name: str) -> None:
        """
        Deletes a bucket.
        Used when a client closes their account.

        Args:
            bucket_name (str): bucket to be deleted.
        """
        try:
            bucket = self.storage_client.get_bucket(bucket_name)
            bucket.delete()
        except exceptions.NotFound:
            log.error(f"Bucket {bucket_name} not found.")
        except exceptions.Conflict:
            for blob in self.list_blobs_in_bucket(bucket_name):
                self.delete_blob(bucket_name, blob)

    def list_buckets(self) -> list[str]:
        """
        Lists all buckets in a project.

        Returns:
            list[str]:: List of all buckets in a project
        """
        buckets = self.storage_client.list_buckets()
        return [bucket.name for bucket in buckets]

    def write_blob_to_bucket(
        self,
        input_text: str,
        bucket_name: str,
    ) -> None:
        """
        Writes a string into a blob in a bucket.

        Args:
            input_text (str): String to write into a bucket.
            bucket_name (str): Bucket to write a string to.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob_name = ""  # TODO: define blob naming
        blob = bucket.blob(blob_name)
        try:
            blob.upload_from_string(input_text)
            log.info(f"String uploaded to gs://{bucket_name}/{blob_name}")
        except exceptions.GoogleCloudError as e:
            log.error(e)

    def read_blob_from_bucket(self, uri: str) -> str:
        """
        Reads a string-like blob from bucket.

        Args:
            uri (str): URI to read string from

        Returns:
            str: String.
        """
        bucket_name, blob_name = self.get_bucket_and_blob_from_uri(uri)
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        try:
            return blob.download_as_string()
        except Exception as e:
            print(e)

    def list_blobs_in_bucket(self, bucket_name: str) -> list[str]:
        """
        Lists all blobs in a given bucket.

        Args:
            bucket_name (str): Bubket name to list blobs in.

        Returns:
            list[str]: List of URIs.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        return [blob.name for blob in blobs]

    def delete_blob(self, uri: str) -> None:
        """
        Deletes a blob from the bucket.

        Args:
            bucket_name (str): Bucket name.
            blob_name (str): Blob name.
        """
        bucket_name, blob_name = self.get_bucket_and_blob_from_uri(uri)
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            log.warning(f"Blob {blob_name} deleted in bucket: {bucket_name}.")
            blob.delete()
        except exceptions.NotFound:
            log.error(f"Blob {blob_name} not found.")

    @staticmethod
    def get_bucket_and_blob_from_uri(uri: str) -> str:
        """
        Extracts bucket name and blob name from an URI using regexp.

        Args:
            uri (str): URI to extract bucket name and blob name from

        Raises:
            ValueError: If URI is not a valid URI.

        Returns:
            str: _description_
        """
        pattern = r"gs://(.*?)/(.*)"
        if Google.is_valid_uri(uri):
            return re.match(pattern, uri).groups()
        else:
            raise ValueError(f"{uri} is not a valid URI.")
