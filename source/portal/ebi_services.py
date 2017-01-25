import requests

from django.core.cache import cache


class NoTaxonFoundException(Exception):
    pass


def ebi_get_taxonomy_by_id(taxid):
    payload = {
        'query': 'id:{}'.format(taxid),
        'fields': 'name',
        'format': 'json'
    }
    payload_str = "&".join('%s=%s' % (k, v) for k, v in payload.items())
    response = requests.get('https://www.ebi.ac.uk/ebisearch/ws/rest/taxonomy', params=payload_str)
    json = response.json()
    if 'entries' in json and len(json['entries']):
        return json['entries']
    else:
        raise NoTaxonFoundException("No entries returned for taxid '{}'".format(taxid))


def ebi_search_taxonomy_by_id(taxid):
    cache_key = 'ebi_search_taxonomy_by_id_{}'.format(taxid)
    return cache.get_or_set(cache_key, ebi_get_taxonomy_by_id(taxid))
