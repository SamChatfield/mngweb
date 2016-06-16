from django.http import JsonResponse

from .models import Country


def country_typeahead(request):
    q = request.GET.get('q', '')
    if q:
        matches = (Country.objects
                   .filter(name__icontains=q)
                   .values_list('name', flat=True)[:10])
    else:
        matches = Country.objects.all().values_list('name', flat=True)
    data = list(matches)
    return JsonResponse(data, safe=False)
