import datetime

from django.shortcuts import get_object_or_404, render
from nltk.tokenize import sent_tokenize

from .models import Article, Author, Topic

NUM_OF_LATEST_NEWS = 6
NUM_OF_RECENTLY_ADDED = 7


def index(request):
    index_1 = NUM_OF_LATEST_NEWS
    index_2 = NUM_OF_LATEST_NEWS + NUM_OF_RECENTLY_ADDED
    latest_article_list = Article.objects.order_by("-pub_date")[:index_1]
    recently_added_article_list = Article.objects.order_by("-pub_date")[index_1:index_2]
    topic_list = Topic.objects.all()
    current_year = datetime.datetime.now().year
    context = {
        "latest_article_list": latest_article_list,
        "recently_added_article_list": recently_added_article_list,
        "topic_list": topic_list,
        "current_year": current_year,
        "current_year_3": current_year - 3,
    }
    return render(request, "newsapp/index.html", context)


def detail(request, article_id):
    index_1 = NUM_OF_LATEST_NEWS
    index_2 = NUM_OF_LATEST_NEWS + NUM_OF_RECENTLY_ADDED
    article = get_object_or_404(Article, pk=article_id)
    recently_added_article_list = Article.objects.exclude(
        headline=article.headline
    ).order_by("-pub_date")[index_1:index_2]
    article_text = [sentence for sentence in sent_tokenize(article.article_text)]
    topic_list = Topic.objects.all()
    current_year = datetime.datetime.now().year
    return render(
        request,
        "newsapp/detail.html",
        {
            "article": article,
            "article_text": article_text,
            "recently_added_article_list": recently_added_article_list,
            "topic_list": topic_list,
            "current_year": current_year,
            "current_year_3": current_year - 3,
        },
    )


def author(request, author_name_surname):
    index_1 = NUM_OF_LATEST_NEWS
    index_2 = NUM_OF_LATEST_NEWS + NUM_OF_RECENTLY_ADDED
    author_articles = Article.objects.filter(author=author_name_surname).order_by(
        "-pub_date"
    )
    author = get_object_or_404(Author, name_surname=author_name_surname)
    recently_added_article_list = Article.objects.exclude(
        author=author.name_surname
    ).order_by("-pub_date")[index_1:index_2]
    topic_list = Topic.objects.all()
    current_year = datetime.datetime.now().year
    return render(
        request,
        "newsapp/author.html",
        {
            "author_articles": author_articles,
            "recently_added_article_list": recently_added_article_list,
            "author_name_surname": author_name_surname,
            "author": author,
            "topic_list": topic_list,
            "current_year": current_year,
            "current_year_3": current_year - 3,
        },
    )


def topic(request, topic_name):
    index_1 = NUM_OF_LATEST_NEWS
    index_2 = NUM_OF_LATEST_NEWS + NUM_OF_RECENTLY_ADDED
    topic_articles = Article.objects.filter(topic=topic_name).order_by("-pub_date")
    topic = get_object_or_404(Topic, name=topic_name)
    recently_added_article_list = Article.objects.order_by("-pub_date")[index_1:index_2]
    topic_list = Topic.objects.all()
    current_year = datetime.datetime.now().year
    current_year_3 = datetime.datetime.now().year - 3
    return render(
        request,
        "newsapp/topic.html",
        {
            "topic_articles": topic_articles,
            "recently_added_article_list": recently_added_article_list,
            "topic_name": topic_name,
            "topic": topic,
            "topic_list": topic_list,
            "current_year": current_year,
            "current_year_3": current_year - 3,
        },
    )
