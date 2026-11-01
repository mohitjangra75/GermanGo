"""Shared abstract models.

Courses and the enquiry inbox are the only tables of our own, both managed
in the admin. The rest of the site's content lives in each app's
``content.py``.
"""

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
