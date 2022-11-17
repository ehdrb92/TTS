from django.urls import path

from .views import ProjectAPI, get_audio_list, update_text

urlpatterns = [
    path("project/", ProjectAPI.as_view()),
    path("audio/", get_audio_list),
    path("audio/<int:project_id>/", update_text),
]
