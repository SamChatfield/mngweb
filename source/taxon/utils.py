import csv

from .models import Taxon


def load_taxon_data(file_path):
    """clear and reload Taxon data from csv"""
    Taxon.objects.all().delete()
    reader = csv.DictReader(open(file_path))
    for row in reader:
        taxon = Taxon(fm_id=row['taxon_id'], name=row['name'],
                      data_set=row['data_set'])
        taxon.save()
