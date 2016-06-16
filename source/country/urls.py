from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^typeahead/$', views.country_typeahead, name='country_typeahead'),
]
