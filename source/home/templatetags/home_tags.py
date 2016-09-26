import datetime
import requests

from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.http import urlquote
from statistics import median_low

from ..models import NavigationMenu, ServicePrice, Testimonial,\
    PeoplePagePerson, PERSON_TEAM_CHOICES
from portal.services import limsfm_request


register = template.Library()


# LIMS stats (RESTFM)

def update_lims_sample_stats():
    # find samples with related strain aliquot
    url = (settings.RESTFM_BASE_URL +
           'layout/sample_api.json?RFMkey=' +
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
        else:
            return {}
    except Exception:
        return {}


def update_lims_project_stats():
    today = datetime.datetime.today()
    start_date = (today - datetime.timedelta(90))
    try:
        response = limsfm_request(
            'layout/project_api',
            'get',
            {
                'RFMmax': 1,
                'RFMsF1': 'data_sent_date',
                'RFMsV1': '>={}/{}'.format(start_date.month, start_date.year),
            })
        if response.status_code == 200:
            project_stats = {}
            wait_time_string = (response.json()['data'][0]
                                ['summary_list_wait_time_weeks'])
            wait_time_list = [int(i) for i in wait_time_string.splitlines()]
            project_stats['median_wait_time_weeks'] = median_low(
                wait_time_list
            )
            return project_stats
        else:
            return {}
    except Exception:
        return {}


@register.assignment_tag(takes_context=False)
def get_lims_sample_stats():
    return cache.get_or_set(
        'lims_sample_stats',
        update_lims_sample_stats(),
        settings.LIMS_STATS_CACHE_TIMEOUT
    )


@register.assignment_tag(takes_context=False)
def get_lims_project_stats():
    return cache.get_or_set(
        'lims_project_stats',
        update_lims_project_stats(),
        settings.LIMS_STATS_CACHE_TIMEOUT
    )


# Navigation menus

@register.simple_tag(takes_context=False)
def get_navigation_menu(menu_name):
    menu = NavigationMenu.objects.filter(menu_name=menu_name)

    if menu:
        return menu[0].menu_items.all()
    else:
        return None


# Person feed by team

@register.simple_tag(takes_context=False)
def people_feed_by_team():
    result = []
    for t in PERSON_TEAM_CHOICES:
        people = PeoplePagePerson.objects.filter(team=t[0])
        if people:
            team = {}
            team['code'] = t[0]
            team['name'] = t[1]
            team['people'] = people
            result.append(team)
    return result


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
