import csv
from datetime import datetime
from pathlib import Path
import requests

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string

from ipware.ip import get_real_ip
from netaddr import IPNetwork, IPAddress
from django_slack import slack_message

from .models import EnvironmentalSampleType, HostSampleType
from .tasks import mngvariants

def handle_limsfm_request_exception(request, e):
    ERROR_MESSAGE = ("The MicrobesNG customer portal is temporarily "
                     "unavailable. Please try again later.")
    messages.error(request, ERROR_MESSAGE)
    slack_message('portal/slack/limsfm_request_exception.slack',
                  {'e': e, 'path': request.path})
    print(e)
    return 503  # http status


def handle_limsfm_http_exception(request, e):
    ERROR_MESSAGE = ("An unexpected error has occured. "
                     "Please contact info@microbesng.uk")
    if e.response.status_code == 404:
        raise Http404
    else:
        messages.error(request, ERROR_MESSAGE)
        slack_message('portal/slack/limsfm_http_exception.slack',
                      {'e': e, 'path': request.path})
    print(e)
    return 500  # http status


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


def form_errors_to_json(request, form):
    for nfe in form.non_field_errors():
        messages.error(request, nfe)
    json = messages_to_json(request)
    json['errors'] = form.errors
    return json


def json_messages_or_redirect(request, url, status=200):
    if request.is_ajax():
        return JsonResponse(messages_to_json(request), status=status)
    return HttpResponseRedirect(url)


def request_should_post_to_slack(request):
    ip = get_real_ip(request)
    if not ip:
        return True  # do post for dev server (no 'real' external ip)
    try:
        ignore_networks = getattr(settings, 'SLACK_LOG_IGNORE_NETWORKS', None)
    except AttributeError:
        return True
    return not any(IPAddress(ip) in IPNetwork(n) for n in ignore_networks)


def user_is_project_owner(user, project):
    user_email = getattr(user, 'email', None)
    if not user_email:
        return False
    return user_email.lower() == project['primary_contact']['email'].lower()


def user_is_project_contact(user, project):
    user_email = getattr(user, 'email', None)
    if not user_email:
        return False
    return user_email.lower() in [c['email'].lower() for c in project['contacts']]


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


def variants_zip_exists(zip_url):
    res = requests.head(zip_url)
    return res.status_code == 200


def get_variant_calling_status(project_uuid, results_url_secure):
    """
    Check the status of the variant calling task for project_uuid

    Return indication of whether it is:
    - NOT_REQUESTED
    - IN_PROGRESS
    - COMPLETE
    - FAILED
    """
    variants_zip_url = '{}variants_new.zip'.format(results_url_secure)
    zip_exists = variants_zip_exists(variants_zip_url)

    task_res = mngvariants.AsyncResult(project_uuid)
    task_state = task_res.state
    print('Retrieved celery task with ID: {}, STATE: {}'.format(task_res.id, task_state))
    print('Variants zip exists?: {}'.format(zip_exists))

    if task_state == 'SUCCESS':
        # If the task reports success then double check that the variants zip exists in S3
        if zip_exists:
            return 'COMPLETE'
        else:
            return 'FAILED'
    elif task_state == 'PENDING':
        # If the task reports pending but the results zip exists then it is complete
        if zip_exists:
            return 'COMPLETE'
        else:
            return 'NOT_REQUESTED'
    else:
        # Otherwise, use the mapping from task state mapping
        state_map = {
            'PENDING': 'NOT_REQUESTED',
            'STARTED': 'IN_PROGRESS',
            'SUCCESS': 'COMPLETE',
            'FAILURE': 'FAILED'
        }
        return state_map[task_state]


def gmo_flag_to_file(project_reference, signer_name, gmo_flag):
    """Write the reference, signer_name, timestamp and gmo_flag to a TSV file in ~/.mngweb_gmo/"""
    # Directory in which all GMO flag files are placed, create it if it doesn't already exist
    gmo_flag_dir = Path('~/.mngweb_gmo/').expanduser()
    gmo_flag_dir.mkdir(exist_ok=True)

    # The file for this project
    gmo_flag_file = gmo_flag_dir / '{}.txt'.format(project_reference)

    # Get current time in ISO 8601 format (UTC)
    timestamp = datetime.utcnow().isoformat() + 'Z'

    # Write a single tab-separated line with the reference and the flag to the file
    with open(str(gmo_flag_file), 'a') as f:
        line = '\t'.join([project_reference, signer_name, timestamp, gmo_flag])
        f.write('{}\n'.format(line))
