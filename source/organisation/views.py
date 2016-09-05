from django.http import JsonResponse

from .models import Organisation


def organisation_typeahead(request):
    q = request.GET.get('q', '')
    if q:
        matches = (Organisation.objects
                   .filter(name__icontains=q)
                   .values_list('name', flat=True)[:10])
    else:
        matches = Organisation.objects.all().values_list('name', flat=True)
    data = list(matches)
    return JsonResponse(data, safe=False)
