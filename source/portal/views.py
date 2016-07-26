import requests

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest,\
    HttpResponseRedirect, JsonResponse, Http404

from openpyxl.writer.excel import save_virtual_workbook
from django_slack import slack_message

from .forms import EmailLinkForm, ProjectLineForm, UploadSampleSheetForm
from .models import EnvironmentalSampleType, HostSampleType
from .sample_sheet import create_sample_sheet, parse_sample_sheet
from .services import limsfm_email_project_links, limsfm_get_project,\
    limsfm_update_projectline, limsfm_bulk_update_projectlines,\
    limsfm_get_contact
from .utils import messages_to_json


def handle_limsfm_request_exception(request, e):
    ERROR_MESSAGE = ("The MicrobesNG customer portal is temporarily "
                     "unavailable. Please try again later.")
    messages.error(request, ERROR_MESSAGE)
    slack_message('portal/slack/limsfm_request_exception.slack',
                  {'e': e, 'path': request.path})

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
        slack_message('portal/slack/limsfm_http_exception.slack',
                      {'e': e, 'path': request.path})

    if request.is_ajax():
        return JsonResponse(messages_to_json(request), status=500)
    else:
        return render(request, 'portal/project.html')


def customer_projects(request, customer_uuid):
    try:
        customer = limsfm_get_contact(customer_uuid)
    except requests.HTTPError as e:
        return handle_limsfm_http_exception(request, e)
    except requests.RequestException as e:
        return handle_limsfm_request_exception(request, e)
    else:
        return render(
            request, 'portal/customer_projects.html', {'customer': customer})


def project_detail(request, uuid):
    try:
        project = limsfm_get_project(uuid)
    except requests.HTTPError as e:
        return handle_limsfm_http_exception(request, e)
    except requests.RequestException as e:
        return handle_limsfm_request_exception(request, e)
    else:
        slack_message('portal/slack/limsfm_project_detail_access.slack',
                      {'project': project})
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
                slack_message('portal/slack/limsfm_projectline_update.slack',
                              {'form': form})
                messages.success(request, "Saved")
                return JsonResponse(messages_to_json(request))
        else:
            for nfe in form.non_field_errors():
                messages.error(request, nfe)
            json = messages_to_json(request)
            json['errors'] = form.errors
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


def download_sample_sheet(request, uuid):
    wb = create_sample_sheet(uuid)
    response = HttpResponse(
        content=save_virtual_workbook(wb),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=microbesng_sample_sheet.xlsx'
    return response


def upload_sample_sheet(request, uuid):
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

        # Get project, index lines by sample ref
        try:
            project = limsfm_get_project(uuid)
        except requests.HTTPError as e:
            return handle_limsfm_http_exception(request, e)
        except requests.RequestException as e:
            return handle_limsfm_request_exception(request, e)

        # Parse sample sheet
        parsed = parse_sample_sheet(project, sheet)

        # Errors found
        errors = parsed['errors']
        if errors:
            for e in errors[0:3]:  # Only report first 3
                m = ("Error on ROW %(row)d: %(message)s" %
                     {'row': e['row'] + 1, 'message': e['message']})
                messages.error(request, m)
            return HttpResponseRedirect(
                reverse('project_detail', args=[uuid]))

        # Bulk update via API
        try:
            limsfm_bulk_update_projectlines(uuid, parsed['updates'])
        except requests.HTTPError as e:
            return handle_limsfm_http_exception(request, e)
        except requests.RequestException as e:
            return handle_limsfm_request_exception(request, e)

        # Report success
        update_count = len(parsed['updates'])
        slack_message(
            'portal/slack/limsfm_upload_sample_sheet_success.slack',
            {'project': project, 'update_count': update_count})
        messages.success(
            request,
            "%(count)d rows successfully imported." %
            {'count': update_count}
        )
        return HttpResponseRedirect(reverse('project_detail', args=[uuid]))

    else:
        # Not POST
        return HttpResponseBadRequest()


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
