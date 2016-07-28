from django.utils import timezone

from portal.services import limsfm_get_countries
from .models import Country


def update_countries():
    """update country data via. the LIMSfm api"""
    print("Fetching countries from LIMSfm...")
    try:
        countries = limsfm_get_countries()
    except Exception as e:
        print("An exception occured: %s" % e)

    print("Updating local database table...")
    created_count = 0
    updated_count = 0
    start_time = timezone.now()
    for country in countries:
        updated_values = {
            'iso2': country['iso2_id'],
            'iso3': country['iso3'],
            'name': country['name'],
            'phone_country_code': country['phone_country_code'],
            'phone_trunk_code': country['phone_trunk_code'],
        }
        obj, created = Country.objects.update_or_create(
            iso2=country['iso2_id'],
            defaults=updated_values)
        if created:
            created_count += 1
        else:
            updated_count += 1
    delete_set = Country.objects.filter(updated__lt=start_time)
    deleted_count = len(delete_set)
    delete_set.delete()

    print("Countries update completed. %d created, %d updated, %d deleted." %
          (created_count, updated_count, deleted_count))
