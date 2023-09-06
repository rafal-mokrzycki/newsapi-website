from gcp.gcp_handler import GCP_Handler
from news_handler.news_handler import NewsHandler
from parsers.article_parser import ArticleParser
from writer.ai_writer import AI_Writer


class Director:
    def get_articles_dict(self) -> dict:
        """Returns raw articles dictionary, as taken from NewsHandler."""
        news_handler = NewsHandler()
        return news_handler.get_headlines_custom()

    def unpack_articles_dict(self):
        article_parser = ArticleParser()
        articles_dict = self.get_articles_dict()
        articles_all = articles_dict["articles"]
        urls = articles_all["url"]
        headlines = articles_all["title"]
        articles = article_parser.get_original_article_text(url_to_search=urls, limit=3)
        return urls, headlines, articles

    def rewrite(self):
        urls, headlines, articles = self.unpack_articles_dict()
        gcs = GCP_Handler()
        uris, r_headlines, r_articles = [], [], []
        for headline, article in zip(headlines, articles):
            ai_writer = AI_Writer(headline, article)
            topic = ai_writer.detect_topic(ai_writer.get_named_entities())
            uris.append(gcs.get_uri_from_topic(topic))
            r_headlines.append(ai_writer.rewrite_headline())
            r_articles.append(ai_writer.rewrite_article())
        return urls, uris, r_headlines, r_articles

    def post(headline: str, article: str, image: str):
        ...


def main():
    director = Director()
    # 1. Get N newest articles (urls and headlines) (`news_handler.py`)
    # 2a. Scrape given urls to get full article texts (`article_parser.py`)
    # 2b. Format and filter raw article texts (`article_parser.py`)
    # 3a. Rewrite articles and headlines (`ai_writer.py`)
    # 3b. Get article main topic (`ai_writer.py`)
    # 3c. Get a photo from Google Storage that correspondents to the article main topic (`ai_writer.py` + `gcp_handler.py`)
    # 4a. Return rewritten article text, rewritten headline and an image from Google Storage (...)
    _, uris, r_headlines, r_articles = director.rewrite()

    # 4b. Reformat rewritten article text, inserting html code for advertisment (...)

    # 4c. Post article + headline + image (...)


if __name__ == "__main__":
    main()
