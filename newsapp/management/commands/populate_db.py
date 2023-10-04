import repackage
from django.core.management.base import BaseCommand

from newsapp.models import Author, Topic

repackage.up(3)
from src.config.config import load_config

config = load_config()


class Command(BaseCommand):
    help = "Create topics and authors and save them in the database"

    def handle(self, *args, **options):
        for author_name in config["django"]["authors"]:
            try:
                # Try to get the author from the database
                author = Author.objects.get(name_surname=author_name)
            except Author.DoesNotExist:
                # If the author doesn't exist, create it
                image_url = (
                    "images/authors/" + author_name.lower().replace(" ", "_") + ".jpg"
                )
                author = Author(name_surname=author_name, image=image_url)
                author.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Author {Author.name_surname} successfully posted"
                    )
                )
        for topic_name in config["django"]["topics"]:
            try:
                # Try to get the author from the database
                topic = Topic.objects.get(name=topic_name)
            except Topic.DoesNotExist:
                # If the author doesn't exist, create it
                topic = Topic(name=topic_name)
                topic.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Topic {Topic.name} successfully posted")
                )
