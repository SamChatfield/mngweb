from django.http import JsonResponse

from .models import Taxon


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
