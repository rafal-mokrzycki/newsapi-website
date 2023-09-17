import datetime
from pathlib import Path

import repackage
import requests

from news_handler.exception import NewsAPIException

from ..config.config import load_config
from .news_auth import NewsApiAuth

# from newsapi.newsapi_exception import NewsAPIException


repackage.up(1)
from utils.utils import stringify_date_param
from utils.validators import NewsHandlerValidator

config = load_config()


class NewsHandler(object):
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
        self.auth = NewsApiAuth(api_key=api_key)
        if session is None:
            self.request_method = requests
        else:
            self.request_method = session

    @staticmethod
    def customize_output(func):
        """
        Wrapper for get_top_headlines() and get_everything() for outputting only list
        of tuples of url and title (=headline)
        """

        def wrapper(*args, **kwargs):
            api_results = func(*args, **kwargs)
            final_results = []
            for result in api_results["articles"]:
                final_results.append((result["url"], result["title"]))
            return final_results

        return wrapper

    @customize_output
    def get_top_headlines(  # noqa: C901
        self,
        q: str | None = None,
        qintitle: str | None = None,
        sources: str | None = None,
        language: str = "en",
        country: str | None = None,
        category: str | None = None,
        page_size: int | None = None,
        page: int | None = None,
    ):
        """
        Call the `/top-headlines` endpoint.

        Fetch live top and breaking headlines.

        This endpoint provides live top and breaking headlines for a country,
        specific category in a country, single source, or multiple sources.
        You can also search with keywords.  Articles are sorted by the earliest
        date published first.

        Args:
            q (str | None, optional): Keywords or a phrase to search for in
            the article title and body.  See the official News API
            `documentation <https://newsapi.org/docs/endpoints/everything>`_
            for search syntax and examples.

            qintitle (str | None, optional): Keywords or a phrase to search
            for in the article title and body.  See the official News API
            `documentation <https://newsapi.org/docs/endpoints/everything>`_
            for search syntax and examples.

            sources (str | None, optional):  A comma-seperated string of identifiers
            for the news sources or blogs you want headlines from.
            Use :meth:`NewsApiClient.get_sources` to locate these programmatically,
            or look at the
            `sources index <https://newsapi.org/sources>`_.
            **Note**: you can't mix this param with the
            ``country`` or ``category`` params.

            language (str, optional): The 2-letter ISO-639-1 code of the language
            you want to get headlines for.
            See :data:`newsapi.const.languages` for the set of allowed values.
            The default for this method is ``"en"`` (English).
            **Note**: this parameter is not mentioned in the
            `/top-headlines documentation
            <https://newsapi.org/docs/endpoints/top-headlines>`_ as of Sep. 2019,
            but *is* supported by the API. Defaults to "en".

            country (str | None, optional): The 2-letter ISO 3166-1 code of the country
            you want to get headlines for.
            See :data:`newsapi.const.countries` for the set of allowed values.
            **Note**: you can't mix this parameter with the ``sources`` param.

            category (str | None, optional): The category you want to get headlines for.
            See :data:`newsapi.const.categories` for the set of allowed values.
            **Note**: you can't mix this parameter with the ``sources`` param.

            page_size (_type_, optional): Use this to page through the results
            if the total results found is
            greater than the page size.

            page (_type_, optional): The number of results to return per page (request).
            20 is the default, 100 is the maximum.

        Raises:
            NewsAPIException: If the ``"status"`` value of the response is ``"error"``
            rather than ``"ok"``.

        Returns:
            dict: JSON response as nested Python dictionary.
        """

        payload = {}

        # Keyword/Phrase
        if q is not None:
            if NewsHandlerValidator.is_valid_string(q):
                payload["q"] = q
            else:
                raise TypeError("keyword/phrase q param should be of type str")

        # Keyword/Phrase in Title
        if qintitle is not None:
            if NewsHandlerValidator.is_valid_string(qintitle):
                payload["qintitle"] = qintitle
            else:
                raise TypeError("keyword/phrase qintitle param should be of type str")

        # Sources
        if (sources is not None) and ((country is not None) or (category is not None)):
            raise ValueError("cannot mix country/category param with sources param.")

        # Sources
        if sources is not None:
            if NewsHandlerValidator.is_valid_string(sources):
                payload["sources"] = sources
            else:
                raise TypeError("sources param should be of type str")

        # Language
        if language is not None:
            if NewsHandlerValidator.is_valid_string(language):
                if language in config["newsapi"]["languages"]:
                    payload["language"] = language
                else:
                    raise ValueError("invalid language")
            else:
                raise TypeError("language param should be of type str")

        # Country
        if country is not None:
            if NewsHandlerValidator.is_valid_string(country):
                if country in config["newsapi"]["countries"]:
                    payload["country"] = country
                else:
                    raise ValueError("invalid country")
            else:
                raise TypeError("country param should be of type str")

        # Category
        if category is not None:
            if NewsHandlerValidator.is_valid_string(category):
                if category in config["newsapi"]["categories"]:
                    payload["category"] = category
                else:
                    raise ValueError("invalid category")
            else:
                raise TypeError("category param should be of type str")

        # Page Size
        if page_size is not None:
            if type(page_size) == int:
                if 0 <= page_size <= 100:
                    payload["pageSize"] = page_size
                else:
                    raise ValueError("page_size param should be an int between 1 and 100")
            else:
                raise TypeError("page_size param should be an int")

        # Page
        if page is not None:
            if type(page) == int:
                if page > 0:
                    payload["page"] = page
                else:
                    raise ValueError("page param should be an int greater than 0")
            else:
                raise TypeError("page param should be an int")

        # Send Request
        r = self.request_method.get(
            config["newsapi"]["top_headlines_url"],
            auth=self.auth,
            timeout=30,
            params=payload,
        )

        # Check Status of Request
        if r.status_code != requests.codes.ok:
            raise NewsAPIException(r.json())

        return r.json()

    @customize_output
    def get_everything(  # noqa: C901
        self,
        q: str | None = None,
        qintitle: str | None = None,
        sources: str | None = None,
        domains: str | None = "cnn",
        exclude_domains: str | None = None,
        from_param: str | datetime.datetime | datetime.date | int | float | None = None,
        to: str | datetime.datetime | datetime.date | int | float | None = None,
        language: str | None = None,
        sort_by=None,
        page: int | None = None,
        page_size: int | None = None,
    ):
        """
        _summary_

        Args:
            q (str | None, optional): Keywords or a phrase to search for
            in the article title and body.  See the official News API
            `documentation <https://newsapi.org/docs/endpoints/everything>`_
            for search syntax and examples.

            qintitle (str | None, optional): Keywords or a phrase to search
              for in the article title and body.  See the official News API
            `documentation <https://newsapi.org/docs/endpoints/everything>`_
            for search syntax and examples.

            sources (str | None, optional):  A comma-seperated string of identifiers
            for the news sources or blogs you want headlines from.
            Use :meth:`NewsApiClient.get_sources` to locate these programmatically,
            or look at the
            `sources index <https://newsapi.org/sources>`_.
            **Note**: you can't mix this param with the
            ``country`` or ``category`` params.

            domains (str | None, optional):  A comma-seperated string of domains
            (eg bbc.co.uk, techcrunch.com, engadget.com)
            to restrict the search to.

            exclude_domains (str | None, optional): A comma-seperated string of domains
            (eg bbc.co.uk, techcrunch.com, engadget.com)
            to remove from the results.

            from_param (str | datetime.datetime | datetime.date | int | float | None,
            optional): A date and optional time for the oldest article allowed.
            If a str, the format must conform to ISO-8601 specifically as one of either
            ``%Y-%m-%d`` (e.g. *2019-09-07*) or ``%Y-%m-%dT%H:%M:%S``
            (e.g. *2019-09-07T13:04:15*).
            An int or float is assumed to represent a Unix timestamp.
              All datetime inputs are assumed to be UTC.

            to (str | datetime.datetime | datetime.date | int | float | None, optional):
              A date and optional time for the newest article allowed.
            If a str, the format must conform to ISO-8601 specifically as one of either
            ``%Y-%m-%d`` (e.g. *2019-09-07*) or ``%Y-%m-%dT%H:%M:%S``
            (e.g. *2019-09-07T13:04:15*).
            An int or float is assumed to represent a Unix timestamp.
            All datetime inputs are assumed to be UTC.

            language (str, optional): The 2-letter ISO-639-1 code of the language
            you want to get headlines for.
            See :data:`newsapi.const.languages` for the set of allowed values.
            The default for this method is ``"en"`` (English).
            **Note**: this parameter is not mentioned in the
            `/top-headlines documentation
            <https://newsapi.org/docs/endpoints/top-headlines>`_ as of Sep. 2019,
            but *is* supported by the API. Defaults to "en".

            sort_by (str | None, optional): The order to sort articles in.
            See :data:`newsapi.const.sort_method` for the set of allowed values.

            page_size (_type_, optional): Use this to page through the results
            if the total results found is
            greater than the page size.

            page (_type_, optional): The number of results to return per page (request).
            20 is the default, 100 is the maximum.

        Raises:
            NewsAPIException: If the ``"status"`` value of the response is ``"error"``
            rather than ``"ok"``.

        Returns:
            dict: JSON response as nested Python dictionary.
        """

        payload = {}

        # Keyword/Phrase
        if q is not None:
            if NewsHandlerValidator.is_valid_string(q):
                payload["q"] = q
            else:
                raise TypeError("keyword/phrase q param should be of type str")

        # Keyword/Phrase in Title
        if qintitle is not None:
            if NewsHandlerValidator.is_valid_string(qintitle):
                payload["qintitle"] = qintitle
            else:
                raise TypeError("keyword/phrase qintitle param should be of type str")

        # Sources
        if sources is not None:
            if NewsHandlerValidator.is_valid_string(sources):
                payload["sources"] = sources
            else:
                raise TypeError("sources param should be of type str")

        # Domains To Search
        if domains is not None:
            if NewsHandlerValidator.is_valid_string(domains):
                payload["domains"] = domains
            else:
                raise TypeError("domains param should be of type str")

        if exclude_domains is not None:
            if isinstance(exclude_domains, str):
                payload["excludeDomains"] = exclude_domains
            else:
                raise TypeError("exclude_domains param should be of type str")

        # Search From This Date ...
        if from_param is not None:
            payload["from"] = stringify_date_param(from_param)

        # ... To This Date
        if to is not None:
            payload["to"] = stringify_date_param(to)

        # Language
        if language is not None:
            if NewsHandlerValidator.is_valid_string(language):
                if language not in config["newsapi"]["languages"]:
                    raise ValueError("invalid language")
                else:
                    payload["language"] = language
            else:
                raise TypeError("language param should be of type str")

        # Sort Method
        if sort_by is not None:
            if NewsHandlerValidator.is_valid_string(sort_by):
                if sort_by in config["newsapi"]["sort_method"]:
                    payload["sortBy"] = sort_by
                else:
                    raise ValueError("invalid sort")
            else:
                raise TypeError("sort_by param should be of type str")

        # Page Size
        if page_size is not None:
            if type(page_size) == int:
                if 0 <= page_size <= 100:
                    payload["pageSize"] = page_size
                else:
                    raise ValueError("page_size param should be an int between 1 and 100")
            else:
                raise TypeError("page_size param should be an int")

        # Page
        if page is not None:
            if type(page) == int:
                if page > 0:
                    payload["page"] = page
                else:
                    raise ValueError("page param should be an int greater than 0")
            else:
                raise TypeError("page param should be an int")

        # Send Request
        r = self.request_method.get(
            config["newsapi"]["everything_url"],
            auth=self.auth,
            timeout=30,
            params=payload,
        )

        # Check Status of Request
        if r.status_code != requests.codes.ok:
            raise NewsAPIException(r.json())

        return r.json()

    def get_sources(
        self,
        category: str | None = None,
        language: str | None = None,
        country: str | None = None,
    ):  # noqa: C901
        """
        Call the `/sources` endpoint.

        Fetch the subset of news publishers that /top-headlines are available from.

        Args:
            category (str | None, optional): Find sources that display news
            of this category.
            See :data:`newsapi.const.categories` for the set of allowed values.

            language (str | None, optional): Find sources that display news
            in a specific language.
            See :data:`newsapi.const.languages` for the set of allowed values.

            country (str | None, optional): Find sources that display news
            in a specific country.
            See :data:`newsapi.const.countries` for the set of allowed values.


        Raises:
            NewsAPIException: If the ``"status"`` value of the response is ``"error"``
            rather than ``"ok"``.

        Returns:
            dict: JSON response as nested Python dictionary.
        """

        payload = {}

        # Language
        if language is not None:
            if NewsHandlerValidator.is_valid_string(language):
                if language in config["newsapi"]["languages"]:
                    payload["language"] = language
                else:
                    raise ValueError("invalid language")
            else:
                raise TypeError("language param should be of type str")

        # Country
        if country is not None:
            if NewsHandlerValidator.is_valid_string(country):
                if country in config["newsapi"]["countries"]:
                    payload["country"] = country
                else:
                    raise ValueError("invalid country")
            else:
                raise TypeError("country param should be of type str")

        # Category
        if category is not None:
            if NewsHandlerValidator.is_valid_string(category):
                if category in config["newsapi"]["categories"]:
                    payload["category"] = category
                else:
                    raise ValueError("invalid category")
            else:
                raise TypeError("category param should be of type str")

        # Send Request
        r = self.request_method.get(
            config["newsapi"]["sources_url"], auth=self.auth, timeout=30, params=payload
        )

        # Check Status of Request
        if r.status_code != requests.codes.ok:
            raise NewsAPIException(r.json())

        return r.json()

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
