import logging
import pathlib
import random
import re
from pathlib import Path

import repackage
from google.cloud import exceptions, storage

repackage.up()
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account

from config.config import load_config
from utils.validators import Google

config = load_config()

PROJECT_ID = ""


class BQ_Handler:
    def __init__(
        self,
        key_path: Path | None = None,
    ) -> None:
        if key_path is None:
            self.key_path = config["key_path"]
        else:
            self.key_path = key_path
        self.credentials = service_account.Credentials.from_service_account_file(
            self.key_path
        )
        self.project_name = config["project_name"]
        self.bigquery_client = bigquery.Client(
            self.project_name, credentials=self.credentials
        )
        self.table = config["target_table"]
        self.dataset = config["target_dataset"]
        self.location = config["location"]

    def if_table_exists(self, dataset: str = None, table: str = None) -> bool:
        """
        Returns true if table with this name exists.

        Args:
            dataset (str, optional): Dataset name. Defaults to None.
            table (str, optional): Table name. Defaults to None.

        Returns:
            bool: True if table exists, False otherwise.
        """
        if dataset is None:
            dataset = self.dataset
        if table is None:
            table = self.table
        try:
            table_id = f"{self.project_name}.{dataset}.{table}"
            self.client.get_table(table_id)
            return True
        except NotFound:
            return False
