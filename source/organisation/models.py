from __future__ import unicode_literals

from django.db import models


class Organisation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
