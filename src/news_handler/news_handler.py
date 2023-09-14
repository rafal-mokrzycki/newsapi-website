import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException

DOMAINS = "cnn.com"
LANGUAGE = "en"
COUNTRY = "us"
HOURS_AGO = 250
LIMIT = 2  # how many articles to return


# TODO: rewrite as own module
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
    ) -> list[tuple[str]]:
        """
        Gets headlines by NewsAPI based on user's preferences.

        Returns:
            list[tuple[str]]: List of tuples (URL, headline)
        """
        from_date = datetime.now() - timedelta(hours=HOURS_AGO)
        try:
            api_results = self.get_everything(
                from_param=from_date,
                language=self.language,
                domains=DOMAINS,
                page=1,
                page_size=LIMIT,
            )
            final_results = []
            for result in api_results["articles"]:
                final_results.append((result["url"], result["title"]))
            return final_results
        except NewsAPIException as e:
            logging.error(e)

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
