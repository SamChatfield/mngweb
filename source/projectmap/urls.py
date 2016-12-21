from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.countries_served, name='countries_served'),
]
