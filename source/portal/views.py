import requests
import django_excel as excel

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest, HttpResponseRedirect,\
    HttpResponseServerError, JsonResponse
from .forms import EmailLinkForm, ProjectLineForm, UploadSampleSheetForm
from .models import EnvironmentalSampleType, HostSampleType
from .services import limsfm_email_project_links, limsfm_get_project,\
    limsfm_update_projectline, limsfm_bulk_update_projectlines


SAMPLE_SHEET_COL_ORDER = [
    'well',
    'sample_ref',
    'customers_ref',
    'dna_concentration_ng_ul',
    'volume_ul',
    'taxon_name',
    'collection_day',
    'collection_month',
    'collection_year',
    'geo_country_name',
    'geo_specific_location',
    'lab_experiment_type',
    'further_details',
    'host_taxon_name',
    'host_sample_type',
    'further_details',
    'environmental_sample_type',
    'further_details',
]


def upload_sample_sheet(request, uuid):
    FAILURE_MESSAGE = ("We're experiencing some problems right now, "
                       "please try again later.")

    if request.method == "POST":
        form = UploadSampleSheetForm(request.POST, request.FILES)
        if form.is_valid():
            filehandle = request.FILES['file']
            sheet = filehandle.get_sheet()

            errors = []
            projectlines = []

            for row in sheet.row_range()[6:102]:
                record_data = dict(zip(SAMPLE_SHEET_COL_ORDER, sheet.row[row]))

                if not record_data['customers_ref']:
                    continue

                try:
                    if record_data['lab_experiment_type']:
                        record_data['study_type'] = 'Lab'
                    elif record_data['host_taxon_name']:
                        record_data['study_type'] = 'Host'
                    elif record_data['environmental_sample_type']:
                        record_data['study_type'] = 'Environmental'
                except KeyError:
                    messages.error(request, "Template file not recognised")
                    return HttpResponseRedirect(
                        reverse('project_detail', args=[uuid]))

                pl_form = ProjectLineForm(record_data)
                if pl_form.is_valid():
                    projectlines.append(pl_form.cleaned_data)
                else:
                    for i, col in enumerate(pl_form.errors):
                        message = (
                            "Import error on ROW %(row)d (%(sample_ref)s):"
                            " %(error)s" %
                            {
                                'row': row,
                                'sample_ref': record_data['sample_ref'],
                                'error': pl_form.errors[col][0]
                            }
                        )
                        errors.append(message)
                        if len(errors) == 3:
                            break
                if len(errors) == 3:
                            break
            if errors:
                for m in errors:
                    messages.error(request, m)
                return HttpResponseRedirect(
                    reverse('project_detail', args=[uuid]))

            try:
                response = limsfm_bulk_update_projectlines(
                    uuid, projectlines)
                status_code = response.status_code
                print(status_code)
            except requests.exceptions.RequestException:
                status_code = 500

            if status_code != 200:
                messages.error(request, FAILURE_MESSAGE)
                return HttpResponseRedirect(
                    reverse('project_detail', args=[uuid]))

            messages.success(
                request,
                "%(count)d rows successfully imported." %
                {'count': len(projectlines)}
            )
            return HttpResponseRedirect(
                reverse('project_detail', args=[uuid]))

        else:
            # Upload form error
            return HttpResponseBadRequest()
    else:
        # Not POST
        return HttpResponseBadRequest()


def project_detail(request, uuid):
    FAILURE_MESSAGE = ("We're experiencing some problems right now, "
                       "please try again later.")

    try:
        project = limsfm_get_project(uuid)
    except Exception:
        messages.error(request, FAILURE_MESSAGE)
        return render(request, 'portal/project.html')

    upload_sample_sheet_form = UploadSampleSheetForm

    return render(
        request, 'portal/project.html',
        {
            'project': project,
            'upload_sample_sheet_form': upload_sample_sheet_form
        })


def projectline_update(request, uuid):
    SUCCESS_MESSAGE = "Saved"
    FAILURE_MESSAGE = "An unexpected error occurred"

    if request.method == 'POST' and request.is_ajax():
        form = ProjectLineForm(request.POST)

        if form.is_valid():
            try:
                api_response = limsfm_update_projectline(uuid, form.cleaned_data)
                status = api_response.status_code
            except requests.exceptions.RequestException:
                status = 500

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
    SUCCESS_MESSAGE = "Thanks! Your project links should arrive in " \
        "your inbox shortly."
    FAILURE_MESSAGE = "We're experiencing some problems right now, " \
        "please try again later."

    if request.method == 'POST':
        # honeypot
        if len(request.POST.get('url_h', '')):
            messages.success(request, SUCCESS_MESSAGE)
            return HttpResponseRedirect(reverse('project_email_link'))

        form = EmailLinkForm(request.POST)

        if form.is_valid():
            try:
                api_response = limsfm_email_project_links(
                    form.cleaned_data['email'])
                status = api_response.status_code
                messages.success(request, SUCCESS_MESSAGE)
            except requests.exceptions.RequestException:
                status = 408
                messages.error(request, FAILURE_MESSAGE)

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
