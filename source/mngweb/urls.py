from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView

from wagtail.contrib.wagtailsitemaps.views import sitemap
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from country import urls as country_urls
from organisation import urls as organisation_urls
from portal import urls as portal_urls
from projectmap import urls as projectmap_urls
from taxon import urls as taxon_urls

from search import views as search_views


urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url('^sitemap\.xml$', sitemap),
    url(r'^robots\.txt/$', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),

    url(r'^search/$', search_views.search, name='search'),

    url(r'country/', include(country_urls)),
    url(r'organisation/', include(organisation_urls)),
    url(r'portal/', include(portal_urls)),
    url(r'projectmap/', include(projectmap_urls, namespace='projectmap')),
    url(r'taxon/', include(taxon_urls)),

    url(r'^accounts/', include('allauth.urls')),

    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic import TemplateView

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
