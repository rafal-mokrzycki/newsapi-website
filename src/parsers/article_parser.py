import logging
import re

from newspaper import Article
from newspaper.article import ArticleException


def get_original_article_text(url: str, headline: str, filter_: bool = True) -> str:
    """
    Gets article text.

    Args:
        url (str): Article URL.
        headline (str): Original headline.
        filter_ (bool): Whether to apply a filter or not.

    Returns:
        str: Headline and original article text (filtered).
    """
    article = Article(url=url)
    try:
        article.download()
    except ArticleException:
        logging.error("Article not properly downloaded")
        return headline, None
    article.parse()
    if article.text == "":
        logging.error("Article not properly downloaded")
        return headline, None
    else:
        logging.info("Article downloaded")
    if filter_:
        article_text = filter_text(article.text)
    else:
        article_text = article.text
    return headline, article_text


def filter_text(article_raw_text: str, filter_: list[str] | None = None) -> str:
    """
    Replaces unnecessary words with empty strings and double newline characters with
    whitespaces.

    Args:
        article_raw_text (str): Article to filter.
        filter_ (list[str] | None, optional): List of regexp patterns to replace.
        Defaults to None.

    Returns:
        str: Filtered article.
    """
    if filter_ is None:
        filter_ = [r"\bad(vert(is(e)?ment)?)?s?\b"]

    for pattern in filter_:
        article_raw_text = re.sub(
            pattern=pattern, repl="", string=article_raw_text, flags=re.I
        )

    return article_raw_text.replace("\n", "").replace("  ", " ")
