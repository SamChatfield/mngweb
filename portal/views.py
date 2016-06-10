import requests

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import formset_factory
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import urlencode

from .forms import EmailLinkForm, ProjectLineForm
from .models import Taxon


def taxon_search(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        matches = Taxon.objects.filter(name__icontains=q)[:10]
        data = []
        for taxon in matches:
            taxon_dct = {}
            taxon_dct['id'] = taxon.fm_id
            taxon_dct['label'] = taxon.name
            taxon_dct['value'] = taxon.name
            data.append(taxon_dct)
        return JsonResponse(data, safe=False)
    else:
        data = {'error': 'Ajax only'}
        return JsonResponse(data, status=400)


def project_detail(request, uuid):
    failure_message = "We're experiencing some problems right now, " \
                      "please try again later."

    ProjectLineFormSet = formset_factory(ProjectLineForm, extra=0)

    # make project api request
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
        projectlines.append({
            'id': pl['projectline_id'],
            'well_alpha': pl['Aliquot::unstored_well_position_display'],
            'sample_ref': pl['Sample::reference'],
            'aliquottype_name': pl['Aliquot::unstored_aliquottype_name'],
            'customers_ref': pl['Sample::customers_ref'],
            'taxon_name': pl['Taxon::name'],
            'queue_name': pl['Queue::name'],
        })

    project['pl_formset'] = ProjectLineFormSet(initial=projectlines)
    print(project['pl_formset'])

    return render(request, 'portal/project.html',
                  {
                      'project': project,
                  }
                  )


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
            # make api request
            url = (settings.RESTFM_BASE_URL +
                   'script/contact_email_project_links/REST.json?' +
                   urlencode({
                       'RFMkey': settings.RESTFM_KEY,
                       'RFMscriptParam': form.cleaned_data.get('email'),
                   })
                   )
            try:
                api_response = requests.get(url, timeout=5)
                status = api_response.status
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
