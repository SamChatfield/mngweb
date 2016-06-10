from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^projects/email-link/$', views.project_email_link, name='project_email_link'),
    url(r'^projects/(?P<uuid>[-\w]{36})/$', views.project_detail, name='project_detail'),
    url(r'^taxon/search/', views.taxon_search, name='taxon_search'),
]
