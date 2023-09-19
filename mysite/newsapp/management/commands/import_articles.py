import datetime

from django.core.management.base import BaseCommand

from newsapp.models import Article, Author


class Command(BaseCommand):
    help = "Import articles into the database"

    def handle(self, *args, **options):
        b = Article(
            headline="This is a headline",
            article_text="This is a text",
            image=r"images/IMG_20190721_184456_j9BYTDf.jpg",
            author=Author.objects.get(name_surname="Jordan Price"),
            topic="economy",
            pub_date=datetime.datetime.now(),
        )
        b.save()
        self.stdout.write(self.style.SUCCESS("Successfully imported the article"))
