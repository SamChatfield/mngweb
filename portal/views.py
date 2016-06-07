import requests

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.http import urlencode

from .forms import EmailLinkForm


def email_link(request):
    success_message = "Thanks! Your project links should arrive in \
                      your inbox shortly"
    failure_message = "We're experiencing some problems right now, \
                      please try again later"

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
            try:
                requests.get(url, timeout=5)
                messages.success(request, success_message)
            except Exception:
                messages.error(request, failure_message)
            return HttpResponseRedirect(reverse('email_link'))
    else:
        form = EmailLinkForm()

    return render(request, 'portal/email_link.html', {'form': form})
