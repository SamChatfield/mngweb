from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^projects/email-link/$',
        views.project_email_link,
        name='project_email_link'),
    url(r'^projects/(?P<uuid>[-\w]{36})/$',
        views.project_detail,
        name='project_detail'),
    url(r'^projects/(?P<uuid>[-\w]{36})/projectlines/update/$',
        views.projectline_update,
        name='projectline_update'),
    url(r'^hostsampletype/typeahead/$',
        views.hostsampletype_typeahead,
        name='hostsampletype_typeahead'),
    url(r'^environmentalsampletype/typeahead/$',
        views.environmentalsampletype_typeahead,
        name='environmentalsampletype_typeahead'),
]
