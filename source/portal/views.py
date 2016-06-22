import requests

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import urlencode

from .forms import EmailLinkForm, ProjectLineForm
from .models import EnvironmentalSampleType, HostSampleType
from .services import limsfm_get_project, limsfm_update_projectline


def project_detail(request, uuid):
    FAILURE_MESSAGE = ("We're experiencing some problems right now, "
                       "please try again later.")

    try:
        project = limsfm_get_project(uuid)
    except Exception:
        messages.error(request, FAILURE_MESSAGE)
        return render(request, 'portal/project.html')

    return render(request, 'portal/project.html', {'project': project})


def projectline_update(request, uuid):
    SUCCESS_MESSAGE = "Saved"
    FAILURE_MESSAGE = "An unexpected error occurred"

    if request.method == 'POST' and request.is_ajax():
        form = ProjectLineForm(request.POST)

        if form.is_valid():
            try:
                api_response = limsfm_update_projectline(form.cleaned_data)
                # print(api_response.text)
                status = api_response.status_code
            except requests.exceptions.RequestException:
                status = 408

            if status == 200:
                messages.success(request, SUCCESS_MESSAGE)
            else:
                messages.error(request, FAILURE_MESSAGE)

            response_data = {'messages': []}
            for message in messages.get_messages(request):
                response_data['messages'].append({
                    "level": message.level,
                    "level_tag": message.level_tag,
                    "message": message.message,
                })
            response_data['messages_html'] = render_to_string(
                'includes/messages.html',
                {'messages': messages.get_messages(request)})
            return JsonResponse(response_data, status=status)
        else:
            response_data = {'errors': form.errors}
            return JsonResponse(response_data, status=400)
    else:
        return JsonResponse({'error': 'Bad request'}, status=400)


def project_email_link(request):
    success_message = "Thanks! Your project links should arrive in " \
        "your inbox shortly."
    failure_message = "We're experiencing some problems right now, " \
        "please try again later."

    if request.method == 'POST':
        # honeypot
        if len(request.POST.get('url_h', '')):
            messages.success(request, success_message)
            return HttpResponseRedirect(reverse('project_email_link'))

        form = EmailLinkForm(request.POST)

        if form.is_valid():
            url = (settings.RESTFM_BASE_URL +
                   'script/contact_email_project_links/REST.json?' +
                   urlencode({
                       'RFMkey': settings.RESTFM_KEY,
                       'RFMscriptParam': form.cleaned_data.get('email'),
                   })
                   )
            try:
                api_response = requests.get(url, timeout=5)
                status = api_response.status_code
                messages.success(request, success_message)
            except requests.exceptions.RequestException:
                status = 408
                messages.error(request, failure_message)

            if request.is_ajax():
                # Valid ajax POST
                data = {'messages': []}
                for message in messages.get_messages(request):
                    data['messages'].append({
                        "level": message.level,
                        "level_tag": message.level_tag,
                        "message": message.message,
                    })
                data['messages_html'] = render_to_string(
                    'includes/messages.html',
                    {'messages': messages.get_messages(request)})
                return JsonResponse(data, status=status)
            else:
                # Valid (non-ajax) post
                HttpResponseRedirect(reverse('project_email_link'))

        elif request.is_ajax():
            # Invalid ajax post
            data = {'errors': form.errors}
            return JsonResponse(data, status=400)

    else:
        # GET request
        form = EmailLinkForm()

    return render(request, 'portal/email_link.html', {'form': form})


def hostsampletype_typeahead(request):
    q = request.GET.get('q', '')
    if q:
        matches = (HostSampleType.objects
                   .filter(name__icontains=q)
                   .values_list('name', flat=True)[:10])
    else:
        matches = HostSampleType.objects.all().values_list('name', flat=True)
    data = list(matches)
    return JsonResponse(data, safe=False)


def environmentalsampletype_typeahead(request):
    q = request.GET.get('q', '')
    if q:
        matches = (EnvironmentalSampleType.objects
                   .filter(name__icontains=q)
                   .values_list('name', flat=True)[:10])
    else:
        matches = EnvironmentalSampleType.objects.all().\
            values_list('name', flat=True)
    data = list(matches)
    return JsonResponse(data, safe=False)
