from django.db import models

from core.models import BaseModel


class Project(BaseModel):
    index = models.PositiveIntegerField()
    title = models.CharField(max_length=100)

    class Meta:
        db_table = "project"


class Audio(BaseModel):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    text = models.TextField()
    speed = models.BooleanField(default=False)

    class Meta:
        db_table = "audio"
