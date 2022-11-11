from rest_framework import serializers

from .models import Project, Audio


class ProjectSerializer(serializers.Serializer):
    model = Project
    fields = "__all__"


class AudioSerializer(serializers.Serializer):
    model = Audio
    fields = "__all__"
