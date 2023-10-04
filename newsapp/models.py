"""
Change your models (in models.py).
Run python manage.py makemigrations to create migrations for those changes
Run python manage.py migrate to apply those changes to the database.
"""
from django import template
from django.db import models

from src.config.config import load_config

register = template.Library()
config = load_config()

# TODO: add possibility to add photos from (1) Google Storage and (2) local files \
# and a switch for them to be able to run locally and in cloud


class Topic(models.Model):
    name = models.CharField(
        max_length=100,
        choices=[(topic, topic) for topic in config["django"]["topics"]],
        primary_key=True,
    )

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    name_surname = models.CharField(
        max_length=100,
        choices=[(author, author) for author in config["django"]["authors"]],
        primary_key=True,
    )

    image = models.ImageField(upload_to="images/authors/")

    def __str__(self):
        return self.name_surname


class Article(models.Model):
    headline = models.CharField(max_length=200)
    article_text = models.CharField(max_length=8000)
    image = models.ImageField(upload_to="images/")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline

    @classmethod
    def create(cls, headline, article_text, image, author, topic, pub_date):
        article = cls(
            headline=headline,
            article_text=article_text,
            image=image,
            author=author,
            topic=topic,
            pub_date=pub_date,
        )
        return article
