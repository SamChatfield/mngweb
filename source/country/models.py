from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    iso2 = models.CharField(max_length=2, primary_key=True)
    iso3 = models.CharField(max_length=3)
    name = models.CharField(max_length=100)
    phone_country_code = models.CharField(max_length=3)
    phone_trunk_code = models.CharField(max_length=1)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
