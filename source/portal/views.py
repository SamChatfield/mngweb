import requests

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views.decorators.http import require_POST

from django_slack import slack_message
from openpyxl.writer.excel import save_virtual_workbook
from mngweb.decorators import require_ajax

from .forms import ProjectAcceptTermsForm, EmailLinkForm, ProjectEnaForm, ProjectLineForm, UploadSampleSheetForm
from .models import EnvironmentalSampleType, HostSampleType
from .sample_sheet import create_sample_sheet, parse_sample_sheet
from .services import limsfm_email_project_links, limsfm_get_project,\
    limsfm_update_projectline, limsfm_bulk_update_projectlines,\
    limsfm_get_contact, limsfm_update_project
from .utils import messages_to_json, json_messages_or_redirect, request_should_post_to_slack, form_errors_to_json


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


def customer_projects(request, customer_uuid):
    customer = None
    try:
        customer = limsfm_get_contact(customer_uuid)
    except requests.HTTPError as e:
        handle_limsfm_http_exception(request, e)
    except requests.RequestException as e:
        handle_limsfm_request_exception(request, e)
    finally:
        return render(
            request, 'portal/customer_projects.html', {'customer': customer})


def project_detail(request, uuid):
    # Handle POST
    if request.method == 'POST':
        project_ena_form = ProjectEnaForm(request.POST)
        if project_ena_form.is_valid():
            try:
                limsfm_update_project(uuid, project_ena_form.cleaned_data)
            except requests.HTTPError as e:
                status = handle_limsfm_http_exception(request, e)
            except requests.RequestException:
                status = handle_limsfm_request_exception(request, e)
            else:
                slack_message('portal/slack/limsfm_project_ena_update.slack',
                              {'uuid': uuid, 'form': project_ena_form})
                messages.success(request, "Saved")
                status = 200
            if request.is_ajax():
                return JsonResponse(messages_to_json(request), status=status)
        elif request.is_ajax():
            return JsonResponse(form_errors_to_json(request, project_ena_form), status=400)

    # Fetch project from lims
    project = None
    try:
        project = limsfm_get_project(uuid)
    except requests.HTTPError as e:
        handle_limsfm_http_exception(request, e)
    except requests.RequestException as e:
        handle_limsfm_request_exception(request, e)
    else:
        if not (project['submission_requirements_name'] or
                project['meta_data_status'] == 'Accepted' or
                project['all_content_received_date']):  # Redirect to accept submission requirements
            return HttpResponseRedirect(reverse(project_accept_submission_requirements, args=[uuid]))

    if request.method == 'GET':
        project_ena_form = ProjectEnaForm(initial=project)

    context = {'project': project, 'project_ena_form': project_ena_form}

    if True:  # project['is_confidential'] or project['ena_title']:  # Render full project portal
        if request_should_post_to_slack(request):
            slack_message('portal/slack/limsfm_project_detail_access.slack',
                          {'request': request, 'project': project})
        context['upload_sample_sheet_form'] = UploadSampleSheetForm()
        return render(request, 'portal/project.html', context)
    else:  # Collect ena title/abstract before proceeding to portal
        if request_should_post_to_slack(request):
            slack_message('portal/slack/limsfm_project_setup_access.slack',
                          {'request': request, 'project': project})
        return render(request, 'portal/project_setup.html', context)


def project_accept_submission_requirements(request, uuid):
    if request.method == 'POST':
        form = ProjectAcceptTermsForm(request.POST)
        if form.is_valid():
            try:
                limsfm_update_project(uuid, form.cleaned_data)
            except requests.HTTPError as e:
                handle_limsfm_http_exception(request, e)
            except requests.RequestException:
                handle_limsfm_request_exception(request, e)
            else:
                slack_message('portal/slack/limsfm_project_accepted_submission_requirements.slack',
                              {'uuid': uuid, 'form': form})
                return HttpResponseRedirect(reverse(project_detail, args=[uuid]))
    else:
        form = ProjectAcceptTermsForm()
    # GET request, or invalid/failed POST
    try:
        project = limsfm_get_project(uuid)
    except requests.HTTPError as e:
        handle_limsfm_http_exception(request, e)
    except requests.RequestException as e:
        handle_limsfm_request_exception(request, e)
    return render(
        request, 'portal/accept_submission_requirements.html',
        {
            'project': project,
            'terms_form': form,
        })


@require_POST
@require_ajax
def projectline_update(request, project_uuid, projectline_uuid):
    form = ProjectLineForm(request.POST)
    if form.is_valid():
        try:
            limsfm_update_projectline(project_uuid, projectline_uuid,
                                      form.cleaned_data)
        except requests.HTTPError as e:
            status = handle_limsfm_http_exception(request, e)
        except requests.RequestException as e:
            status = handle_limsfm_request_exception(request, e)
        else:
            slack_message('portal/slack/limsfm_projectline_update.slack',
                          {'form': form})
            messages.success(request, "Saved")
            status = 200
        return JsonResponse(messages_to_json(request), status=status)
    else:
        json = form_errors_to_json(request, form)
        return JsonResponse(json, status=400)


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
                status = handle_limsfm_request_exception(request, e)
            else:
                messages.success(request, SUCCESS_MESSAGE)
                status = 200
            if request.is_ajax():
                return JsonResponse(messages_to_json(request), status=status)
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


@require_POST
def upload_sample_sheet(request, uuid):
    form = UploadSampleSheetForm(request.POST, request.FILES)
    redirect_url = reverse('project_detail', args=[uuid])

    if not form.is_valid():
        messages.error(request, "No file uploaded.")
        return json_messages_or_redirect(request, redirect_url, status=400)

    filehandle = request.FILES['file']

    try:
        sheet = filehandle.get_sheet()
    except NotImplementedError as e:
        messages.error(request, "Invalid file uploaded. Please download the Excel template for your project.")
        return json_messages_or_redirect(request, redirect_url, status=400)

    # Check headers
    if not (
        len(sheet.row[2]) == 18 and
        sheet[2, 17] == 'Further details'
    ):
        messages.error(request, "Invalid sample sheet headers. "
                                "Have you used the correct template?")
        return json_messages_or_redirect(request, redirect_url, status=400)

    # Get project, index lines by sample ref
    try:
        project = limsfm_get_project(uuid)
    except requests.HTTPError as e:
        status = handle_limsfm_http_exception(request, e)
        return JsonResponse(messages_to_json(request), status=status)
    except requests.RequestException as e:
        status = handle_limsfm_request_exception(request, e)
        return JsonResponse(messages_to_json(request), status=status)

    # Parse sample sheet
    parsed = parse_sample_sheet(project, sheet)

    # Errors found
    errors = parsed['errors']
    if errors:
        for e in errors[0:10]:  # Only report first 10
            m = ("Error on row %(row)d: %(message)s" %
                 {'row': e['row'] + 1, 'message': e['message']})
            messages.error(request, m)
        return json_messages_or_redirect(request, redirect_url, status=400)

    # Bulk update via API
    try:
        limsfm_bulk_update_projectlines(uuid, parsed['updates'])
    except requests.HTTPError as e:
        status = handle_limsfm_http_exception(request, e)
    except requests.RequestException as e:
        status = handle_limsfm_request_exception(request, e)
    else:
        status = 200
        update_count = len(parsed['updates'])
        slack_message(
            'portal/slack/limsfm_upload_sample_sheet_success.slack',
            {'project': project, 'update_count': update_count})
        messages.success(
            request,
            "%(count)d rows successfully imported." %
            {'count': update_count}
        )

    # Return
    if request.is_ajax():
        if status == 200:
            json_data = {'redirect_url': redirect_url}
        else:
            json_data = messages_to_json(request)
        return JsonResponse(json_data, status=status)
    else:
        return HttpResponseRedirect(redirect_url)


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
