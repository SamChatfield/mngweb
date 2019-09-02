from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.create_order_link, name='orders_create_order_link'),
    url(r'^(?P<uuid>[-\w]{36})$', views.confirm_order, name='orders_confirm_order'),
]
