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


def project_detail(request, uuid):
    failure_message = "We're experiencing some problems right now, " \
                      "please try again later."

    project_url = (settings.RESTFM_BASE_URL +
                   'layout/project_api.json?' +
                   urlencode({
                       'RFMkey': settings.RESTFM_KEY,
                       'RFMsF1': 'uuid',
                       'RFMsV1': '==' + uuid,
                   })
                   )
    try:
        api_response = requests.get(project_url, timeout=5)
        project = api_response.json()['data'][0]
        projectline_url = (settings.RESTFM_BASE_URL +
                           'layout/projectline_api.json?' +
                           urlencode({
                               'RFMkey': settings.RESTFM_KEY,
                               'RFMsF1': 'project_id',
                               'RFMsV1': project['project_id'],
                               'RFMmax': 0,
                           })
                           )
        api_response = requests.get(projectline_url, timeout=5)
        pl_raw = api_response.json()['data']
    except Exception:
        messages.error(request, failure_message)
        return render(request, 'portal/project.html')

    pl_raw.sort(key=lambda k:
                (
                    k['Container::reference'],
                    int(k['Aliquot::unstored_container_position'])
                    if len(k['Aliquot::unstored_container_position']) else 0,
                    k['Sample::reference'],
                )
                )

    projectlines = []
    for pl in pl_raw:
        data = {
            'id': pl['projectline_id'],
            'well_alpha': pl['Aliquot::unstored_well_position_display'],
            'sample_ref': pl['Sample::reference'],
            'aliquottype_name': pl['Aliquot::unstored_aliquottype_name'],
            'customers_ref': pl['Sample::customers_ref'],
            'taxon': pl['Taxon::name'],
            'queue_name': pl['Queue::name'],
            'volume_ul': pl['Aliquot::volume_ul'],
            'dna_concentration_ng_ul': pl['Aliquot::dna_concentration_ng_ul'],
            'geo_country': pl['sample_Country::name'],
            'geo_specific_location': pl['Sample::geo_specific_location'],
            'collection_day': pl['Sample::collection_day'],
            'collection_month': pl['Sample::collection_month'],
            'collection_year': pl['Sample::collection_year'],
            'study_type': pl['Sample::study_type'],
            'lab_experiment_type': pl['Sample::lab_experiment_type'],
            'environmental_sample_type': pl['Sample::environmental_sample_type'],
            'host_taxon': pl['sample_Taxon#host::name'],
            'host_sample_type': pl['Sample::host_sample_type'],
            'further_details': pl['Sample::further_details'],
        }
        if data['customers_ref']:
            data['form'] = ProjectLineForm(initial=data)
        else:
            data['form'] = ProjectLineForm()
        projectlines.append(data)

    project['projectlines'] = projectlines

    return render(request, 'portal/project.html',
                  {
                      'project': project,
                  }
                  )


def projectline_update(request, uuid):
    success_message = "Saved"
    failure_message = "An unexpected error occurred"

    if request.method == 'POST' and request.is_ajax():
        form = ProjectLineForm(request.POST)

        if form.is_valid():
            url = (settings.RESTFM_BASE_URL +
                   'layout/projectline_api/' +
                   'projectline_id%3D%3D%3D' +
                   str(form.cleaned_data['id']) + '.json?' +
                   urlencode({
                       'RFMkey': settings.RESTFM_KEY,
                   })
                   )
            payload = {
                'data': [
                    {
                        'Sample::customers_ref':
                            form.cleaned_data['customers_ref'],
                        'Sample::taxon_id':
                            form.cleaned_data['taxon'].fm_id,
                        'Aliquot::volume_ul':
                            str(form.cleaned_data['volume_ul']),
                        'Aliquot::dna_concentration_ng_ul':
                            str(form.cleaned_data['dna_concentration_ng_ul']),
                        'Sample::geo_country_iso2_id':
                            form.cleaned_data['geo_country'].iso2,
                        'Sample::geo_specific_location':
                            form.cleaned_data['geo_specific_location'],
                        'Sample::collection_day':
                            form.cleaned_data['collection_day'],
                        'Sample::collection_month':
                            form.cleaned_data['collection_month'],
                        'Sample::collection_year':
                            form.cleaned_data['collection_year'],
                        'Sample::study_type':
                            form.cleaned_data['study_type'],
                        'Sample::lab_experiment_type':
                            form.cleaned_data['lab_experiment_type'],
                        'Sample::host_taxon_id':
                            (form.cleaned_data['host_taxon'].fm_id
                                if form.cleaned_data['host_taxon'] else ''),
                        'Sample::host_sample_type':
                            (form.cleaned_data['host_sample_type'].name
                                if form.cleaned_data['host_sample_type'] else ''),
                        'Sample::environmental_sample_type':
                            (form.cleaned_data['environmental_sample_type'].name
                                if form.cleaned_data['environmental_sample_type'] else ''),
                        'Sample::further_details':
                            form.cleaned_data['further_details'],
                    }
                ]
            }
            try:
                api_response = requests.put(url, json=payload, timeout=5)
                # print(api_response.text)
                status = api_response.status_code
            except requests.exceptions.RequestException:
                status = 408

            if status == 200:
                messages.success(request, success_message)
            else:
                messages.error(request, failure_message)

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
