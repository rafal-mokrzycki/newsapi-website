import repackage

repackage.up(2)
from src.ai_writer.ai_writer import AI_Writer
from src.news_handler.news_handler import NewsHandler
from src.parsers.article_parser import ArticleParser

if __name__ == "__main__":
    news_dictionary = NewsHandler().get_top_headlines()
    articles_raw_texts = ArticleParser().get_raw_article_text()
