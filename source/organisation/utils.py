from django.utils import timezone

from portal.services import limsfm_get_organisations
from .models import Organisation


def update_organisations():
    """update Organisation data via. the LIMSfm api"""
    print("Fetching Organisations from LIMSfm...")
    try:
        organisations = limsfm_get_organisations()
    except Exception as e:
        print("An exception occured: %s" % e)

    print("Updating local database table...")
    created_count = 0
    updated_count = 0
    start_time = timezone.now()
    for org in organisations:
        updated_values = {
            'name': org['name'],
        }
        obj, created = Organisation.objects.update_or_create(
            id=org['organisation_id'],
            defaults=updated_values)
        if created:
            created_count += 1
        else:
            updated_count += 1
    delete_set = Organisation.objects.filter(updated__lt=start_time)
    deleted_count = len(delete_set)
    delete_set.delete()

    print("Organisation update completed. %d created, %d updated, %d deleted." %
          (created_count, updated_count, deleted_count))
