from django.db import models


class Country(models.Model):
    iso2 = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
