"""
Change your models (in models.py).
Run python manage.py makemigrations to create migrations for those changes
Run python manage.py migrate to apply those changes to the database.
"""
import sys

from django.db import models

print(sys.path)


# TODO: add possibility to add photos from (1) Google Storage and (2) local files \
# and a switch for them to be able to run locally and in cloud


class Article(models.Model):
    headline = models.CharField(max_length=200)
    article_text = models.CharField(max_length=8000)
    image = models.ImageField(upload_to="images/")
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article_text


# TODO: move it and make it work
if __name__ == "__main__":
    b = Article(
        headline="This is a headline",
        article_text="This is a text",
        image=r"images\IMG_20170817_194613.jpg",
    )
    b.save()
