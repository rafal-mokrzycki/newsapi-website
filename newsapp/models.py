"""
Change your models (in models.py).
Run python manage.py makemigrations to create migrations for those changes
Run python manage.py migrate to apply those changes to the database.
"""
from django import template
from django.db import models

register = template.Library()


# TODO: add possibility to add photos from (1) Google Storage and (2) local files \
# and a switch for them to be able to run locally and in cloud


class Author(models.Model):
    # TODO: add image field storing author's photo from thispersondoesnotexists
    class NameSurname(models.TextChoices):
        JORDAN = "Jordan Price"
        IAN = "Ian Alvarez"
        WALLACE = "Wallace Castillo"
        KEN = "Ken Sanders"
        BOB = "Bob Patel"
        JAIME = "Jaime Myers"
        ELLA = "Ella Long"
        STACEY = "Stacey Ross"
        WILMA = "Wilma Foster"
        GINA = "Gina Jimenez"

    name_surname = models.CharField(
        max_length=100,
        choices=NameSurname.choices,
        default=NameSurname.JORDAN,
        primary_key=True,
    )

    def __str__(self):
        return self.name_surname


class Article(models.Model):
    headline = models.CharField(max_length=200)
    article_text = models.CharField(max_length=8000)
    image = models.ImageField(upload_to="images/")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
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
