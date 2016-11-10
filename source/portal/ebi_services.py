import requests

from django.core.cache import cache


def ebi_get_taxonomy_by_id(taxid):
    payload = {
        'query': 'id:{}'.format(taxid),
        'fields': 'name',
        'format': 'json'
    }
    payload_str = "&".join('%s=%s' % (k, v) for k, v in payload.items())
    response = requests.get('https://www.ebi.ac.uk/ebisearch/ws/rest/taxonomy', params=payload_str)
    return response.json()['entries']


def ebi_search_taxonomy_by_id(taxid):
    cache_key = 'ebi_search_taxonomy_by_id_{}'.format(taxid)
    return cache.get_or_set(cache_key, ebi_get_taxonomy_by_id(taxid))
