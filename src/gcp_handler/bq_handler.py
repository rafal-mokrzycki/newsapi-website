"""
Basic BigQuery functionalities. If run, creates a dataset and two tables whose names
are stored in config.json file.
"""
import logging
from pathlib import Path

import pandas as pd
from google.cloud import bigquery, exceptions
from google.oauth2 import service_account

from config.config import load_config

config = load_config()


def main():
    bq_handler = BQ_Handler()
    # create dataset if it doesn't exist
    if not bq_handler.if_dataset_exists():
        bq_handler.create_dataset()
    # create small temp table
    if not bq_handler.if_table_exists(table_name=config["gcp"]["small_temp_table"]):
        bq_handler.create_small_temp_table()
    # create large temp table
    if not bq_handler.if_table_exists(table_name=config["gcp"]["large_temp_table"]):
        bq_handler.create_large_temp_table()


class BQ_Handler:
    def __init__(
        self,
        key_path: Path | None = None,
    ) -> None:
        if key_path is None:
            self.key_path = config["gcp"]["key_path"]
        else:
            self.key_path = key_path
        self.credentials = service_account.Credentials.from_service_account_file(
            self.key_path
        )
        self.project_name = config["gcp"]["project_name"]
        self.bigquery_client = bigquery.Client(
            self.project_name, credentials=self.credentials
        )
        self.dataset_name = config["gcp"]["dataset_name"]
        self.location = config["gcp"]["location"]

    def create_dataset(self, *, dataset_name: str | None = None) -> None:
        """
        Create a BigQuery dataset with the given dataset_name.

        Args:
            dataset_name (str | None, optional): Dataset name. Defaults to None. If None
            taken from config.
        """
        dataset_name = self.dataset if dataset_name is None else dataset_name
        client = bigquery.Client()
        dataset_ref = client.dataset(dataset_name)

        dataset = bigquery.Dataset(dataset_ref)
        client.create_dataset(dataset)  # API request

        logging.info(f"Dataset {dataset.dataset_id} created.")

    def create_table(
        self, *, dataset_name: str | None = None, table_name: str | None = None
    ) -> None:
        """
        Create a BigQuery table with two columns: url (string) and headline (string)
        in the specified dataset.

        Args:
            dataset_name (str | None, optional): Dataset name. Defaults to None. If None
            taken from config.
            table_name (str | None, optional): Table name. Defaults to None.

        Raises:
            NameError: If table_name is None.
        """
        dataset_name = self.dataset_name if dataset_name is None else dataset_name
        if table_name is None:
            raise NameError("table_name cannot be None")
        client = bigquery.Client()
        dataset_ref = client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)

        schema = [
            bigquery.SchemaField("url", "STRING"),
            bigquery.SchemaField("headline", "STRING"),
        ]

        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)  # API request

        logging.info(f"Table {table.table_id} created with schema {table.schema}.")

    def drop_table(
        self, *, dataset_name: str | None = None, table_name: str | None = None
    ) -> None:
        """
        Drop a BigQuery table in the specified dataset.

        Args:
            dataset_name (str | None, optional): Dataset name. Defaults to None. If None
            taken from config.
            table_name (str | None, optional): Table name. Defaults to None.

        Raises:
            NameError: If table_name is None.
        """
        dataset_name = self.dataset_name if dataset_name is None else dataset_name
        if table_name is None:
            raise NameError("table_name cannot be None")
        client = bigquery.Client()
        dataset_ref = client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)

        client.delete_table(table_ref)  # API request

        logging.info(f"Table {table_ref.table_id} deleted.")

    def append_data_frame_to_table(
        self,
        *,
        dataset_name: str | None = None,
        table_name: str | None = None,
        data_frame: pd.DataFrame | None = None,
    ) -> None:
        """
        Append a Pandas data_frame to a BigQuery table in the specified dataset.

        Args:
            dataset_name (str | None, optional): Dataset name. Defaults to None. If None
            taken from config.
            table_name (str | None, optional): Table name. Defaults to None.
            data_frame (pd.data_frame | None, optional): Pandas data_frame to append to
            table. Defaults to None.

        Raises:
            NameError: If table_name is None
            NameError: If data_frame is None
        """
        dataset_name = self.dataset if dataset_name is None else dataset_name
        if table_name is None:
            raise NameError("table_name cannot be None")
        if data_frame is None:
            raise NameError("data_frame cannot be None")
        client = bigquery.Client()
        dataset_ref = client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)

        job_config = bigquery.LoadJobConfig()
        job_config.write_disposition = "WRITE_APPEND"

        client.load_table_from_data_frame(data_frame, table_ref, job_config=job_config)

        logging.info(f"Data appended to table {table_ref.table_id}.")

    def delete_record_by_url(
        self,
        *,
        dataset_name: str | None = None,
        table_name: str | None = None,
        url: str | None = None,
    ) -> None:
        """
        Delete a record from a BigQuery table in the specified dataset
        by matching the 'url' column.

        Args:
            dataset_name (str | None, optional): Dataset name. Defaults to None. If None
            taken from config.
            table_name (str | None, optional): Table name. Defaults to None.
            url (str | None, optional): URL (primary key)to delete record with.
            Defaults to None.

        Raises:
            NameError: If table_name set to None
            NameError: If url set to None
        """
        dataset_name = self.dataset_name if dataset_name is None else dataset_name
        if table_name is None:
            raise NameError("table_name cannot be None")
        if url is None:
            raise NameError("url cannot be None")
        client = bigquery.Client()
        dataset_ref = client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)

        query = f"""
        DELETE FROM `{table_ref.project}.{table_ref.dataset_id}.{table_ref.table_id}`
        WHERE url = @url
        """
        job_config = bigquery.QueryJobConfig()
        job_config.query_parameters = [
            bigquery.ScalarQueryParameter("url", "STRING", url)
        ]

        client.query(query, job_config=job_config)  # API request

        logging.info(
            f"Deleted record(s) from table {table_ref.table_id} where url = {url}."
        )

    def if_table_exists(
        self, *, dataset_name: str | None = None, table_name: str | None = None
    ) -> bool:
        """
        Returns true if table with this name exists.

        Args:
            dataset_name (str, optional): Dataset name. Defaults to None.
            table_name (str, optional): Table name. Defaults to None.

        Returns:
            bool: True if table exists, False otherwise.
        """
        if dataset_name is None:
            dataset_name = self.dataset_name
        try:
            table_name = f"{self.project_name}.{dataset_name}.{table_name}"
            self.client.get_table(table_name)
            return True
        except exceptions.NotFound:
            return False

    def if_dataset_exists(self, *, dataset_name: str | None = None) -> bool:
        if dataset_name is None:
            dataset = self.dataset_name
        client = bigquery.Client(project=self.project_name)
        dataset_ref = client.dataset(dataset)
        try:
            # Attempt to fetch the dataset. \
            # This will raise an exception if it doesn't exist.
            client.get_dataset(dataset_ref)
            return True  # Dataset exists
        except exceptions.NotFound:
            return False  # Dataset doesn't exist

    def create_small_temp_table(self):
        dataset_name = self.dataset_name
        table_name = config["small_temp_table"]
        self.create_table(dataset_name=dataset_name, table_name=table_name)

    def create_large_temp_table(self):
        dataset_name = self.dataset_name
        table_name = config["large_temp_table"]
        self.create_table(dataset_name=dataset_name, table_name=table_name)


if __name__ == "__main__":
    main()
