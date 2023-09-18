from django.shortcuts import get_object_or_404, render

from .models import Article


def index(request):
    latest_article_list = Article.objects.order_by("-pub_date")[:6]
    recently_added_article_list = Article.objects.order_by("-pub_date")[6:10]
    context = {
        "latest_article_list": latest_article_list,
        "recently_added_article_list": recently_added_article_list,
    }
    return render(request, "newsapp/index.html", context)


def detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    image = article.image
    return render(request, "newsapp/detail.html", {"article": article, "image": image})
