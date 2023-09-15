"""
Change your models (in models.py).
Run python manage.py makemigrations to create migrations for those changes
Run python manage.py migrate to apply those changes to the database.
"""
from django.db import models


class Article(models.Model):
    headline = models.CharField(max_length=200)
    article_text = models.CharField(max_length=8000)
    image = models.ImageField(upload_to="images/")
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article_text


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
