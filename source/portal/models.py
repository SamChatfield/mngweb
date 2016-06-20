from django.db import models


class HostSampleType(models.Model):
    name = models.CharField(max_length=100)


class EnvironmentalSampleType(models.Model):
    name = models.CharField(max_length=100)
