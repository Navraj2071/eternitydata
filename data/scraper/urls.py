from django.urls import path, include
from scraper import views

urlpatterns = [
    path("run/", views.index),
]
