from django.core.management.base import BaseCommand, CommandError
from organisation.utils import update_organisations


class Command(BaseCommand):
    help = """Updates Organisation records to sync with LIMSfm"""

    def handle(self, *args, **options):
        try:
            update_organisations()
        except Exception as e:
            raise CommandError('An exception occurred: %s' % e)
        else:
            self.stdout.write(self.style.SUCCESS(
                "Successfully updated Organisation records from LIMSfm"))
