from django.db import models


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the object was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Date and time when the object was last updated."
    )

    class Meta:
        abstract = True
