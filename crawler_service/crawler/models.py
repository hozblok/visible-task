from django.db import models


class LinksJobModel(models.Model):
    MAX_URL_LENGTH = 8_192

    url = models.TextField(max_length=MAX_URL_LENGTH)
    status = models.CharField(
        max_length=1,
        choices=(
            ("s", "SUBMITTED"),
            ("i", "IN_PROGRESS"),
            ("d", "DONE"),
            ("e", "ERROR"),
        ),
    )
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
