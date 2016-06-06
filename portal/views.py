import requests

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.http import urlencode

from .forms import EmailLinkForm


def email_link(request):
    if request.method == 'POST':
        form = EmailLinkForm(request.POST)
        if form.is_valid():
            # make api request
            url = (settings.RESTFM_BASE_URL +
                   'script/contact_email_project_links/REST.json?' +
                   urlencode({
                             'RFMkey': settings.RESTFM_KEY,
                             'RFMscriptParam': form.data.get('email'),
                             })
                   )
            messages.info(request, url)
            try:
                response = requests.get(url, timeout=3)
                messages.info(request, response.status_code)
                return HttpResponseRedirect(request.path_info)
            except Exception:
                pass
    else:
        form = EmailLinkForm()

    return render(request, 'portal/email_link.html', {'form': form})
