import requests

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import urlencode

from .forms import EmailLinkForm


def project_detail(request, uuid):
    failure_message = "We're experiencing some problems right now, " \
                      "please try again later."

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
        projectlines = api_response.json()['data']
    except Exception:
        messages.error(request, failure_message)
        return render(request, 'portal/project.html')

    # Django templates can't handle '::' in keys
    for pl in projectlines:
        for key in pl:
            if ':' in key:
                pl[key.replace(':', '_')] = pl.pop(key)
    projectlines.sort(key=lambda k:
                      (
                          k['Container__reference'],
                          int(k['Aliquot__unstored_container_position']),
                          k['Sample__reference'],
                      )
                      )
    print(projectlines)
    project['projectlines'] = projectlines

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
