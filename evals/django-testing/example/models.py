from django.conf import settings
from django.db import models


class Note(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)

    class Meta:
        constraints = [models.CheckConstraint(condition=~models.Q(title=""), name="note_title_not_empty")]
