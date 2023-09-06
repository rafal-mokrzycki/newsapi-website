from news_handler.news_handler import NewsHandler
from parsers.article_parser import ArticleParser
from writer.ai_writer import AI_Writer

if __name__ == "__main__":
    news_dictionary = NewsHandler().get_headlines_custom()
    articles_raw_texts = ArticleParser().get_raw_article_text()
