from django.db import models


class Taxon(models.Model):
    fm_id = models.IntegerField()
    name = models.CharField(max_length=255)
    data_set = models.CharField(max_length=20)
