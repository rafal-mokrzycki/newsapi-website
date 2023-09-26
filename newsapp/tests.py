from django.test import TestCase

from newsapp.models import Article


class ArticleTestCase(TestCase):
    def setUp(self):
        Article.objects.create(
            headline="headline",
            article_text="article_text",
            image=r"images\city_2.jpg",
            author="Gina Jimenez",
            topic="economy",
            pub_date="2023-02-02T23:23:23",
        )

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        article = Article.objects.get(headline="headline")
        self.assertEqual(print(article), "headline")
