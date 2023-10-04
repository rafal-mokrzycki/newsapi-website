from django.conf import settings  # new
from django.conf.urls.static import static  # new
from django.urls import path  # new

from . import views

app_name = "newsapp"

urlpatterns = [
    # ex: /newsapp/
    path("", views.index, name="index"),
    # ex: /newsapp/5/
    path("<int:article_id>/", views.detail, name="detail"),
    # ex: /newsapp/author=/
    path("author=<str:author_name_surname>/", views.author, name="author"),
    # ex: /newsapp/topic=/
    path("topic=<str:topic_name>/", views.topic, name="topic"),
]
if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
