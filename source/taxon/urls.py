from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^typeahead/$', views.taxon_typeahead, name='taxon_typeahead'),
    url(r'^prokaryotes/typeahead/$', views.taxon_prokaryotes_typeahead, name='taxon_prokaryotes_typeahead'),
    url(r'^ebi_typeahead/$', views.ebi_typeahead, name='ebi_typeahead'),
    url(r'^ebi_taxonomy/(?P<taxid>[0-9]+)/$', views.ebi_taxonomy_detail, name='ebi_taxonomy_detail'),
]
