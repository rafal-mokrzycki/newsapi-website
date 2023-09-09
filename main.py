import logging

from src.ai_writer.ai_writer import AI_Writer
from src.gcp_handler.gcp_handler import GCP_Handler
from src.news_handler.news_handler import NewsHandler
from src.parsers.article_parser import ArticleParser

LIMIT = 1
MODES = ["no_gcp"]  # used for running app without GCP access

logging.basicConfig(level=logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger("").addHandler(console)


class Director:
    def __init__(self, mode) -> None:
        self.mode = mode
        logging.info("`Director` initialized")

    def get_articles_dict(self) -> dict:
        """Returns raw articles dictionary, as taken from NewsHandler."""
        news_handler = NewsHandler()
        raw_headlines = news_handler.get_headlines_custom()
        logging.info("`get_articles_dict()` executed - headlines downloaded")
        return raw_headlines

    def unpack_articles_dict(self):
        article_parser = ArticleParser()
        articles_dict = self.get_articles_dict()
        articles_all = articles_dict["articles"]
        urls = [article["url"] for article in articles_all]
        headlines = [article["title"] for article in articles_all]
        articles = article_parser.get_original_article_text(
            url_to_search=urls, limit=LIMIT
        )
        logging.info("`unpack_articles_dict()` executed")
        return urls, headlines, articles

    def rewrite(self):
        # TODO: order
        urls, headlines, articles = self.unpack_articles_dict()
        if self.mode != "no_gcp":
            gcs = GCP_Handler()
        uris, r_headlines, r_articles = [], [], []
        for headline, article in zip(headlines, articles):
            ai_writer = AI_Writer(headline=headline, article=article, mode=self.mode)
            topic = ai_writer.detect_topic()
            if self.mode == "no_gcp":
                uris.append(f"gs://sample-uri/{topic}")
            else:
                uris.append(gcs.get_uri_from_topic(topic))
            r_headlines.append(ai_writer.rewrite_headline())
            r_articles.append(ai_writer.rewrite_article())
        return urls, uris, r_headlines, r_articles

    def post(headline: str, article: str, image: str):
        ...


def main(mode="no_gcp"):
    director = Director(mode=mode)
    # 1. Get N newest articles (urls and headlines) (`news_handler.py`)
    # 2a. Scrape given urls to get full article texts (`article_parser.py`)
    # 2b. Format and filter raw article texts (`article_parser.py`)
    # 3a. Rewrite articles and headlines (`ai_writer.py`)
    # 3b. Get article main topic (`ai_writer.py`)
    # 3c. Get a photo from Google Storage that correspondents to the article main topic (`ai_writer.py` + `gcp_handler.py`)
    # 4a. Return rewritten article text, rewritten headline and an image from Google Storage (...)
    _, uris, r_headlines, r_articles = director.rewrite()
    print(len(uris))
    print(r_headlines)
    # 4b. Reformat rewritten article text, inserting html code for advertisment (...)

    # 4c. Post article + headline + image (...)


if __name__ == "__main__":
    main()
