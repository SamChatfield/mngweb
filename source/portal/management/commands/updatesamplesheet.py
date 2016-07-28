from django.core.management.base import BaseCommand, CommandError
from portal.sample_sheet import update_sample_sheet_template


class Command(BaseCommand):
    help = """Updates the sample sheet excel template with the
              latest lookup data (taxonomy, countries etc.)"""

    def handle(self, *args, **options):
        try:
            update_sample_sheet_template()
        except Exception as e:
            raise CommandError('An exception occurred: %s' % e)
        else:
            self.stdout.write(self.style.SUCCESS(
                "Successfully updated sample sheet excel template"))
