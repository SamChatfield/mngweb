import json

from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import mark_safe
from requests import RequestException

from portal.services import limsfm_get_project_countries_served


register = template.Library()


@register.inclusion_tag('projectmap/tags/map_countries_served.html')
def map_countries_served(container_id='projectmap_container', arc=False, height=None,
                         projection='equirectangular', responsive=False):
    countries = cache.get_or_set(
        'projectmap_countries_served',
        limsfm_get_project_countries_served(),
        settings.LIMS_STATS_CACHE_TIMEOUT
    )

    map_data = {}
    arc_data = []
    for c in countries:
        iso3 = c['iso3']
        map_data[iso3] = {'fillKey': 'served'}
        if iso3 != 'GBR':
            arc_data.append({'origin': iso3, 'destination': 'GBR'})

    map_json = mark_safe(json.dumps(map_data))
    arc_json = mark_safe(json.dumps(arc_data)) if arc else None
    return({
        'container_id': container_id,
        'countries': countries,
        'map_json': map_json,
        'arc_json': arc_json,
        'height': height,
        'projection': projection,
        'responsive': responsive,
    })


@register.simple_tag
def countries_served():
    try:
        return cache.get_or_set(
            'projectmap_countries_served',
            limsfm_get_project_countries_served(),
            settings.LIMS_STATS_CACHE_TIMEOUT
        )
    except RequestException as e:
        return None
