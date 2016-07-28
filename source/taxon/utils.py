from django.utils import timezone

from portal.services import limsfm_get_taxonomy
from .models import Taxon


def update_taxonomy():
    """update taxon data via. the LIMSfm api"""
    print("Fetching latest taxonomy from LIMSfm...")
    try:
        taxonomy = limsfm_get_taxonomy()
    except Exception as e:
        print("An exception occured: %s" % e)

    print("Updating local database table...")
    created_count = 0
    updated_count = 0
    start_time = timezone.now()
    for taxon in taxonomy:
        updated_values = {
            'name': taxon['name'],
            'data_set': taxon['data_set']
        }
        obj, created = Taxon.objects.update_or_create(
            fm_id=taxon['taxon_id'],
            defaults=updated_values)
        if created:
            created_count += 1
        else:
            updated_count += 1
    delete_set = Taxon.objects.filter(updated__lt=start_time)
    deleted_count = len(delete_set)
    delete_set.delete()

    print("Taxonomy update completed. %d created, %d updated, %d deleted." %
          (created_count, updated_count, deleted_count))
