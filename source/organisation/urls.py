from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^typeahead/$', views.organisation_typeahead, name='organisation_typeahead'),
]
