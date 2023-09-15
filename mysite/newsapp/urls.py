from django.urls import path

from . import views

app_name = "newsapp"

urlpatterns = [
    # ex: /newsapp/
    path("", views.index, name="index"),
    # ex: /newsapp/5/
    path("<int:article_id>/", views.detail, name="detail"),
]
