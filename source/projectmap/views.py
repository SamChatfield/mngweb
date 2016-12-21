from django.shortcuts import render


def countries_served(request):
    return render(request, 'projectmap/map_countries_served.html')
