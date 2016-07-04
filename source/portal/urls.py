from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^projects/email-link/$',
        views.project_email_link,
        name='project_email_link'),
    url(r'^projects/(?P<uuid>[-\w]{36})/$',
        views.project_detail,
        name='project_detail'),
    url(r'^projects/(?P<project_uuid>[-\w]{36})/projectlines/(?P<projectline_uuid>[-\w]{36})/update/$',
        views.projectline_update,
        name='projectline_update'),
    url(r'^projects/(?P<uuid>[-\w]{36})/download_sample_sheet/$',
        views.download_sample_sheet,
        name='download_sample_sheet'),
    url(r'^projects/(?P<uuid>[-\w]{36})/upload_sample_sheet/$',
        views.upload_sample_sheet,
        name='upload_sample_sheet'),
    url(r'^hostsampletype/typeahead/$',
        views.hostsampletype_typeahead,
        name='hostsampletype_typeahead'),
    url(r'^environmentalsampletype/typeahead/$',
        views.environmentalsampletype_typeahead,
        name='environmentalsampletype_typeahead'),
]
