import csv

from .models import EnvironmentalSampleType, HostSampleType


def load_environmentalsampletype_data(file_path):
    """clear and reload EnvironmentalSampleType data from csv"""
    EnvironmentalSampleType.objects.all().delete()
    reader = csv.DictReader(open(file_path))
    for row in reader:
        obj = EnvironmentalSampleType(name=row['name'])
        obj.save()


def load_hostsampletype_data(file_path):
    """clear and reload HostSampleType data from csv"""
    HostSampleType.objects.all().delete()
    reader = csv.DictReader(open(file_path))
    for row in reader:
        obj = HostSampleType(name=row['name'])
        obj.save()
