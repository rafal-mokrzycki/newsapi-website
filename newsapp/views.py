from django.shortcuts import get_object_or_404, render
from nltk.tokenize import sent_tokenize

from .models import Article, Author

NUM_OF_LATEST_NEWS = 6
NUM_OF_RECENTLY_ADDED = 7


def index(request):
    index_1 = NUM_OF_LATEST_NEWS
    index_2 = NUM_OF_LATEST_NEWS + NUM_OF_RECENTLY_ADDED
    latest_article_list = Article.objects.order_by("-pub_date")[:index_1]
    recently_added_article_list = Article.objects.order_by("-pub_date")[index_1:index_2]
    context = {
        "latest_article_list": latest_article_list,
        "recently_added_article_list": recently_added_article_list,
    }
    return render(request, "newsapp/index.html", context)


def detail(request, article_id):
    index_1 = NUM_OF_LATEST_NEWS
    index_2 = NUM_OF_LATEST_NEWS + NUM_OF_RECENTLY_ADDED
    article = get_object_or_404(Article, pk=article_id)
    recently_added_article_list = Article.objects.order_by("-pub_date")[index_1:index_2]
    article_text = [sentence for sentence in sent_tokenize(article.article_text)]
    return render(
        request,
        "newsapp/detail.html",
        {
            "article": article,
            "article_text": article_text,
            "recently_added_article_list": recently_added_article_list,
        },
    )


def author(request, author_name_surname):
    index_1 = NUM_OF_LATEST_NEWS
    index_2 = NUM_OF_LATEST_NEWS + NUM_OF_RECENTLY_ADDED
    author_articles = Article.objects.filter(author=author_name_surname).order_by(
        "-pub_date"
    )
    author = get_object_or_404(Author, name_surname=author_name_surname)
    recently_added_article_list = Article.objects.order_by("-pub_date")[index_1:index_2]
    return render(
        request,
        "newsapp/author.html",
        {
            "author_articles": author_articles,
            "recently_added_article_list": recently_added_article_list,
            "author_name_surname": author_name_surname,
            "author": author,
        },
    )
