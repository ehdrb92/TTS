from django.urls import path

from .views import ProjectAPI, AudioAPI

urlpatterns = [
    path("project/", ProjectAPI.as_view()),
    path("audio/", AudioAPI.as_view()),
]
