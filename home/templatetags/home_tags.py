import requests

from django import template
from django.conf import settings
from django.core.cache import cache
from statistics import median_low

from home.models import NavigationMenu, ServicePrice, Testimonial

register = template.Library()


# LIMS stats (RESTFM)

def update_lims_sample_stats():
    # find samples with related strain aliquot
    url = (settings.RESTFM_BASE_URL +
           'layout/Sample.json?RFMkey=' +
           settings.RESTFM_KEY +
           '&RFMsF1=Aliquot%3A%3Aaliquottype_id&RFMsV1=%3D%3D2' +
           '&RFMmax=1')
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            sample_stats = {}
            sample_stats['strain_count'] = int(
                response.json()['info']['foundSetCount']
            )
            sample_stats['total_count'] = int(
                response.json()['info']['tableRecordCount']
            )
            return sample_stats
    except Exception:
        return None


def update_lims_project_stats():
    url = (settings.RESTFM_BASE_URL +
           'layout/Project.json?RFMkey=' +
           settings.RESTFM_KEY +
           '&RFMmax=1')
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            project_stats = {}
            wait_time_string = (response.json()['data'][0]
                                ['summary_list_wait_time_weeks'])
            wait_time_list = [int(i) for i in wait_time_string.splitlines()]
            project_stats['median_wait_time_weeks'] = median_low(
                wait_time_list
            )
            return project_stats
    except Exception:
        return None


@register.assignment_tag(takes_context=False)
def get_lims_sample_stats():
    return cache.get_or_set(
        'lims_sample_stats',
        update_lims_sample_stats(),
        86400  # 24 hours
    )


@register.assignment_tag(takes_context=False)
def get_lims_project_stats():
    return cache.get_or_set(
        'lims_project_stats',
        update_lims_project_stats(),
        86400  # 24 hours
    )


# Navigation menus

@register.assignment_tag(takes_context=False)
def get_navigation_menu(menu_name):
    menu = NavigationMenu.objects.filter(menu_name=menu_name)

    if menu:
        return menu[0].menu_items.all()
    else:
        return None


# Service price panels for home page

@register.inclusion_tag('home/tags/service_price_panels_homepage.html',
                        takes_context=True)
def service_price_panels_homepage(context):
    return {
        'service_prices': ServicePrice.objects.all(),
        'request': context['request'],
    }


# Testimonial carousel

@register.inclusion_tag('home/tags/testimonial_carousel.html',
                        takes_context=True)
def testimonial_carousel(context):
    return {
        'testimonials': Testimonial.objects.all(),
        'request': context['request'],
    }

