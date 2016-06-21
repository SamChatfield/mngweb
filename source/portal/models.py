from __future__ import unicode_literals

from django.db import models


class HostSampleType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class EnvironmentalSampleType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
