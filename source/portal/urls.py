from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^projects/email-link/$', views.project_email_link, name='project_email_link'),
    url(r'^projects/(?P<uuid>[-\w]{36})/$', views.project_detail, name='project_detail'),
    url(r'^api/taxon/prokaryotes/', views.taxon_api_prokaryotes, name='taxon_api_prokaryotes'),
    url(r'^api/taxon/', views.taxon_api, name='taxon_api'),
]
