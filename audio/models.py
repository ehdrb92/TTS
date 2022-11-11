from django.db import models

from core.models import BaseModel


class Project(BaseModel):
    index = models.PositiveIntegerField()
    project_title = models.CharField(max_length=100)

    class Meta:
        db_name = "project"


class Audio(BaseModel):
    project_id = models.ForeignKey("Project", on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    text = models.TextField()
    speed = models.BooleanField(default=False)

    class Meta:
        db_name = "audio"
