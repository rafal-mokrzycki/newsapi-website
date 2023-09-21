import datetime

import repackage
from django.core.management.base import BaseCommand
from tqdm.auto import tqdm

from newsapp.models import Article, Author

repackage.up(3)
from src.ai.ai_writer import AI_Writer
from src.config.config import load_config
from src.news.news_handler import NewsHandler
from src.parsers import article_parser
from src.utilities.utils import wait_for_web_scraping

config = load_config()


class Command(BaseCommand):
    help = "Create articles and save them in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "mode",
            nargs="?",
            type=str,
            choices=config["django"]["modes"],
            default="local",
        )
        parser.add_argument(
            "page_size", nargs="?", type=int, choices=range(1, 25), default=2
        )

    def handle(self, *args, **options):
        mode = options["mode"]
        news_handler = NewsHandler()
        list_of_urls_and_headlines = news_handler.get_top_headlines(
            sources="cnn", page=1, page_size=options["page_size"]
        )
        for element in tqdm(list_of_urls_and_headlines):
            try:
                headline, article = article_parser.get_original_article_text(
                    element[0], element[1]
                )
                ai_writer = AI_Writer(headline=headline, article=article, mode=mode)
                ai_writer.rewrite_headline()
                ai_writer.rewrite_article()
                ai_writer.detect_topic()
                try:
                    # Try to get the author from the database
                    author = Author.objects.get(name_surname=ai_writer.author)
                except Author.DoesNotExist:
                    # If the author doesn't exist, create it
                    author = Author(name_surname=ai_writer.author)
                    author.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Author {Author.name_surname} successfully posted"
                        )
                    )

                article = Article(
                    headline=ai_writer.rewritten_headline,
                    article_text=ai_writer.rewritten_article,
                    image=ai_writer.uri,
                    author=Author.objects.get(name_surname=ai_writer.author),
                    topic=ai_writer.topic,
                    pub_date=datetime.datetime.now(),
                )
                article.save()
                self.stdout.write(self.style.SUCCESS("Article successfully posted"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
            finally:
                wait_for_web_scraping()
