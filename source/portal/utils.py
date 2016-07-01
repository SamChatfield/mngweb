import csv

from django.contrib import messages
from django.template.loader import render_to_string

from .models import EnvironmentalSampleType, HostSampleType


def messages_to_json(request):
    json = {'messages': []}
    for message in messages.get_messages(request):
        json['messages'].append({
            "level": message.level,
            "level_tag": message.level_tag,
            "message": message.message,
        })
    json['messages_html'] = render_to_string(
        'includes/messages.html',
        {'messages': messages.get_messages(request)})
    return json


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
