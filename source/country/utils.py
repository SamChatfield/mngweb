import csv

from .models import Country


def load_country_data(file_path):
    """clear and reload Country data from csv"""
    Country.objects.all().delete()
    reader = csv.DictReader(open(file_path))
    for row in reader:
        country = Country(iso2=row['iso2'], name=row['name'])
        country.save()
