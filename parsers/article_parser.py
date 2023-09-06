import random
import re
import time

from newspaper import Article


class ArticleParser:
    # def get_raw_article_text(self, news_dictionary: dict, limit: int = 25) -> list[str]:
    #     """
    #     Gets first N article texts from a dictionary returned by NewsAPI.

    #     Args:
    #         news_dictionary (dict): Articles returned by NewsAPI
    #         limit (int, optional): Number of articles to parse. Defaults to 25.

    #     Returns:
    #         _type_: _description_
    #     """
    #     articles = news_dictionary["articles"]
    #     articles_raw_texts = []
    #     for num, _ in enumerate(articles):
    #         url_to_search = articles[num]["url"]
    #         # article_title = articles[num]["title"]
    #         if num > limit:
    #             break
    #         # web scraping
    #         article = Article(url_to_search)
    #         article.parse()
    #         articles_raw_texts.append(article.text)
    #         time_to_sleep = random.choice(list(range(5, 10)))
    #         time.sleep(time_to_sleep)
    #     return articles_raw_texts
    def get_original_article_text(
        self, url_to_search: str | list[str], limit: int = 25
    ) -> str | list[str]:
        """
        Gets article text.

        Args:
            url_to_search (str | list[str]): Article URL or list thereof.
            limit (int, optional): Number of articles to parse. Defaults to 25.

        Returns:
            str | list[str]: Original article or list of original articles.
        """
        if isinstance(url_to_search, list):
            articles_raw_texts = []
            for num, url in enumerate(url_to_search):
                if num > limit:
                    break
                # web scraping
                article = Article(url)
                article.parse()
                articles_raw_texts.append(article.text)
                time_to_sleep = random.choice(list(range(5, 10)))
                time.sleep(time_to_sleep)
            return articles_raw_texts
        else:
            article = Article(url_to_search)
            article.parse()
            return article.text

    def filter_texts(
        self, articles_raw_texts: list[str], filter_: list[str] | None = None
    ) -> list[str]:
        """
        Replaces unnecessary words with empty strings and double newline characters with
        whitespaces.

        Args:
            articles_raw_texts (list[str]): List of articles to filter.
            filter_ (list[str] | None, optional): List of regexp patterns to replace.
            Defaults to None.

        Returns:
            list[str]: List of filtered articles.
        """
        if filter_ is None:
            filter_ = [r"ad(vert(isement)?)?s?"]

        filtered_texts = []
        for raw_text in articles_raw_texts:
            for pattern in filter_:
                filtered_texts.append(re.sub(pattern=pattern, repl="", string=raw_text))
        return [filtered_text.replace("\n", "") for filtered_text in filtered_texts]
