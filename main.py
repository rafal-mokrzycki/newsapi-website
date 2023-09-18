from pathlib import Path

from src.ai_writer.ai_writer import AI_Writer, Filter
from src.news_handler.news_handler import NewsHandler
from src.parsers import article_parser
from src.utils.utils import CustomLogger, wait_for_web_scraping

LIMIT = 1
MODES = ["no_gcp"]  # used for running app without GCP access


logger = CustomLogger(Path(__file__).name)


# TODO: apply changes from maze.py
# TODO: check why named entities are lowercase
def main(mode):
    news_handler = NewsHandler()
    # 1. Get N newest articles (urls and headlines) (`news_handler.py`)
    list_of_urls_and_headlines = news_handler.get_top_headlines()
    for element in list_of_urls_and_headlines:
        # filter out Videos: if 'content' from endpoint /top_headlines contains a video,
        # omit this article
        if Filter.contains_video(element[2]):
            logger.warning(f"Text for `{element[0]}` Contains video. Omitted.")
            continue
        # TODO: check if url was already used
        pass
        # 2a. Scrape given urls to get full article texts (`article_parser.py`)
        # 2b. Format and filter raw article texts (`article_parser.py`)
        headline, article = article_parser.get_original_article_text(
            element[0], element[1]
        )
        if Filter.is_too_short_text(article.text):
            logger.warning(f"Text for `{element[0]}` too short. Omitted.")
            continue
        ai_writer = AI_Writer(headline=headline, article=article, mode=mode)
        # 3a. Rewrite articles and headlines (`ai_writer.py`)
        ai_writer.rewrite_headline()
        ai_writer.rewrite_article()
        # 3b. Get article main topic (`ai_writer.py`)
        # TODO: add functionality assinging URI to AI_Writer variable
        ai_writer.detect_topic()
        # 3c. Get a photo from Google Storage that correspondents to the article main \
        # topic (`ai_writer.py` + `gcp_handler.py`)
        pass
        # 4a. Return rewritten article text, rewritten headline and an image from Google \
        # Storage (...)
        uri, r_headline, r_article = (
            ai_writer.uri,
            ai_writer.rewritten_headline,
            ai_writer.rewritten_article,
        )
        # 4b. Reformat rewritten article text, inserting html code for advertisment (...)
        # TODO: implement
        pass
        # 4c. Post article + headline + image (...)
        # TODO: implement
        pass
        print(uri, r_headline, r_article)
        wait_for_web_scraping()


if __name__ == "__main__":
    main(mode="no_gcp")
