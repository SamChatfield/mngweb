import requests

from django.core.cache import cache
from django.http import JsonResponse

from .models import Taxon
from portal.ebi_services import ebi_search_taxonomy_by_id


def taxon_typeahead(request):
    q = request.GET.get('q', '')
    if q:
        matches = (Taxon.objects
                   .filter(name__icontains=q)
                   .values_list('name', flat=True)[:10])
    else:
        matches = Taxon.objects.all().values_list('name', flat=True)
    data = list(matches)
    return JsonResponse(data, safe=False)


def taxon_prokaryotes_typeahead(request):
    q = request.GET.get('q', '')
    matches = Taxon.objects.filter(data_set__in=['Prokaryotes', 'Other'])
    if q:
        matches = (matches
                   .filter(name__icontains=q)
                   .values_list('name', flat=True)[:10])
    else:
        matches = matches.values_list('name', flat=True)
    data = list(matches)
    return JsonResponse(data, safe=False)


def ebi_typeahead(request):
    cache_key = "ebi_typeahead_?{}".format('&'.join('{}={}'.format(k, v) for k, v in sorted(request.GET.items())))
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)
    try:
        response = requests.get('https://www.ebi.ac.uk/ebisearch/ws/rest/taxonomy', params=request.GET)
    except requests.RequestException:
        JsonResponse({'error': 'An unspecified error occurred.'}, status=500)
    else:
        json = response.json()
        cache.set(cache_key, json)
        return JsonResponse(json)


def ebi_taxonomy_detail(request, taxid):
    try:
        json = ebi_search_taxonomy_by_id(taxid)
    except requests.RequestException:
        JsonResponse({'error': 'An unspecified error occurred.'}, status=500)
    else:
        if json:
            return JsonResponse(json[0])
        else:
            return JsonResponse({'error': 'Taxid {} not found'.format(taxid)}, status=404)
