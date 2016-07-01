import requests
import django_excel as excel

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest, HttpResponseRedirect,\
    HttpResponseServerError, JsonResponse, Http404
from .forms import EmailLinkForm, ProjectLineForm, UploadSampleSheetForm
from .models import EnvironmentalSampleType, HostSampleType
from .services import limsfm_email_project_links, limsfm_get_project,\
    limsfm_update_projectline, limsfm_bulk_update_projectlines
from .utils import messages_to_json


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

        if not form.is_valid():
            messages.error(request, "No file uploaded.")
            return HttpResponseRedirect(reverse('project_detail', args=[uuid]))

        filehandle = request.FILES['file']
        sheet = filehandle.get_sheet()

        # Check headers
        if not (
            len(sheet.row[2]) == 18 and
            sheet[2, 17] == 'Further details'
        ):
            messages.error(request, "Invalid sample sheet headers. "
                                    "Have you used the correct template?")
            return HttpResponseRedirect(
                reverse('project_detail', args=[uuid]))

        # Get project
        try:
            project = limsfm_get_project(uuid)
        except Exception:
            messages.error(request, FAILURE_MESSAGE)
            return HttpResponseRedirect(
                reverse('project_detail', args=[uuid]))

        # Validate each row as form data
        errors = []
        projectlines = []

        for row in sheet.row_range()[6:102]:
            record_data = dict(zip(SAMPLE_SHEET_COL_ORDER, sheet.row[row]))

            # Skip 'blank' rows
            if not record_data['customers_ref']:
                continue

            # Determine 'study_type'
            if record_data.get('lab_experiment_type'):
                record_data['study_type'] = 'Lab'
            elif record_data.get('host_taxon_name'):
                record_data['study_type'] = 'Host'
            elif record_data.get('environmental_sample_type'):
                record_data['study_type'] = 'Environmental'
            else:
                message = (
                    "Import error on ROW %(row)d: Meta data is required"
                    " in one of the 3 coloured sections" % {'row': row}
                )
                errors.append(message)
                continue

            # Pass row data to form
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

        # Errors found
        if errors:
            for m in errors[0:3]:  # Only report first 3
                messages.error(request, m)
            return HttpResponseRedirect(
                reverse('project_detail', args=[uuid]))

        # Bulk update via API
        try:
            response = limsfm_bulk_update_projectlines(
                uuid, projectlines)
            status_code = response.status_code
            print(status_code)
        except requests.exceptions.RequestException:
            status_code = 500

        # Handle API call failure
        if status_code != 200:
            print("Failure %d" % status_code)
            messages.error(request, FAILURE_MESSAGE)
            return HttpResponseRedirect(
                reverse('project_detail', args=[uuid]))

        # Report success
        messages.success(
            request,
            "%(count)d rows successfully imported." %
            {'count': len(projectlines)}
        )
        return HttpResponseRedirect(
            reverse('project_detail', args=[uuid]))

    else:
        # Not POST
        return HttpResponseBadRequest()


def handle_limsfm_request_exception(request, e):
    ERROR_MESSAGE = (
        "The MicrobesNG customer portal is temporarily unavailable. "
        "Please try again later."
    )

    messages.error(request, ERROR_MESSAGE)

    if request.is_ajax():
        return JsonResponse(messages_to_json(request), status=503)
    else:
        return render(request, 'portal/project.html')


def handle_limsfm_http_exception(request, e):
    ERROR_MESSAGE = ("An unexpected error has occured. "
                     "Please contact info@microbesng.uk")

    if e.response.status_code == 404:
        raise Http404
    else:
        messages.error(request, ERROR_MESSAGE)

    if request.is_ajax():
        return JsonResponse(messages_to_json(request), status=500)
    else:
        return render(request, 'portal/project.html')


def project_detail(request, uuid):
    try:
        project = limsfm_get_project(uuid)
    except requests.HTTPError as e:
        return handle_limsfm_http_exception(request, e)
    except requests.RequestException as e:
        return handle_limsfm_request_exception(request, e)
    else:
        return render(
            request, 'portal/project.html',
            {
                'project': project,
                'upload_sample_sheet_form': UploadSampleSheetForm()
            })


def projectline_update(request, project_uuid, projectline_uuid):
    if request.method == 'POST' and request.is_ajax():
        form = ProjectLineForm(request.POST)

        if form.is_valid():
            try:
                limsfm_update_projectline(project_uuid, projectline_uuid,
                                          form.cleaned_data)
            except requests.RequestException as e:
                return handle_limsfm_request_exception(request, e)
            else:
                messages.success(request, "Saved")
                return JsonResponse(messages_to_json(request))
        else:
            json = {'errors': form.errors}
            return JsonResponse(json, status=400)
    else:
        return JsonResponse({'error': 'Bad request'}, status=400)


def project_email_link(request):
    SUCCESS_MESSAGE = (
        "Thanks! Your project links should arrive in your inbox shortly.")

    if request.method == 'POST':
        # Bot honeypot
        if len(request.POST.get('url_h', '')):
            messages.success(request, SUCCESS_MESSAGE)
            return HttpResponseRedirect(reverse('project_email_link'))

        form = EmailLinkForm(request.POST)

        if form.is_valid():
            try:
                limsfm_email_project_links(form.cleaned_data['email'])
            except requests.RequestException as e:
                return handle_limsfm_request_exception(request, e)

            messages.success(request, SUCCESS_MESSAGE)
            if request.is_ajax():
                return JsonResponse(messages_to_json(request))
            else:
                HttpResponseRedirect(reverse('project_email_link'))

        elif request.is_ajax():
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
