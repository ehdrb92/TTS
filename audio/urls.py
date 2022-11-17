from django.urls import path

from .views import (
    ProjectAPI,
    AudioAPI,
)

urlpatterns = [
    path("project/", ProjectAPI.as_view()),
    path("audio/", AudioAPI.as_view()),
    path("audio/<int:project_id>/", AudioAPI.as_view()),
    path("audio/<int:project_id>/<int:index>/", AudioAPI.as_view()),
]
