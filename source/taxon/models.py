from __future__ import unicode_literals

from django.db import models


class Taxon(models.Model):
    fm_id = models.IntegerField()
    name = models.CharField(max_length=255)
    data_set = models.CharField(max_length=20)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
