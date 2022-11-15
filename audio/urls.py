from django.urls import path

from .views import ProjectAPI

urlpatterns = [
    path("project/", ProjectAPI.as_view()),
]
