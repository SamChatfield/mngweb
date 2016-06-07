from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^email-link/$', views.email_link, name='email_link'),
]
