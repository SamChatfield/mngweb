import json

from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import mark_safe

from portal.services import limsfm_get_project_country_codes


register = template.Library()


def update_project_map_data():
    try:
        countries = limsfm_get_project_country_codes()
    except Exception:
        return None
    map_data = {}
    arc_data = []
    for c in countries:
        map_data[c] = {'fillKey': 'served'}
        if c != 'GBR':
            arc_data.append({'origin': c, 'destination': 'GBR'})
    return {
        'map_json': mark_safe(json.dumps(map_data)),
        'arc_json': mark_safe(json.dumps(arc_data))
    }


@register.simple_tag
def get_project_map_data():
    map_data = cache.get_or_set(
        'project_map_data',
        update_project_map_data,
        settings.LIMS_STATS_CACHE_TIMEOUT
    )
    return map_data
