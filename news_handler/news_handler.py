from datetime import datetime, timedelta
from pathlib import Path

import requests
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException

from config.config import log

DOMAINS = "cnn.com"
LANGUAGE = "en"
COUNTRY = "us"
HOURS_AGO = 250


# rewrite as own module
class NewsHandler(NewsApiClient):
    """
    Class for news handling. Enables to collect headlines or whole
    articles, as well as https addresses thereof and images attached
    to them.

    Args:
        NewsApiClient (object): The core client object used to fetch
        data from News API endpoints. See more: https://newsapi.org/docs
    """

    def __init__(self, api_key: str | None = None, session: requests.Session() = None):
        """
        Init function of class NewsHandler.

        Args:
            api_key (str | None, optional): API key. Defaults to None.
            session (requests.Session | None, optional): Session. Defaults to None.
        """
        if api_key is None:
            api_key = self.read_api_key()
        super().__init__(api_key, session)
        self.language = LANGUAGE
        self.country = COUNTRY  # TODO: decide if collect news from other locations

    def get_headlines_custom(
        self,
    ) -> dict:
        """
        Gets headlines by NewsAPI based on user's preferences.

        Args:
            n_headlines (int): Number of headlines to get.

        Returns:
            dict: Nested dictionary with all the gathered information.
        """
        from_date = datetime.now() - timedelta(
            hours=HOURS_AGO
        )  # datetetime 1 hour ago -> HYPERPARAMETER
        try:
            return self.get_everything(
                from_param=from_date, language=self.language, domains=DOMAINS
            )  # domains param should be of type str
        except NewsAPIException as e:
            log.error(e)

    @staticmethod
    def read_api_key(file_name: str = "api.key") -> str:
        """
        Enables to read credentials for NewsAPI from local file.

        Args:
            file_name (str, optional): File name to read the key from.
            Defaults to "api.key".

        Returns:
            str: API key.
        """
        file_path = Path(__file__).parent.joinpath(file_name)
        with open(file_path, "r") as f:
            return str(f.read().splitlines()[0])
