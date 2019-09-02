from __future__ import unicode_literals
import uuid

from django.db import models

class UniqueLink(models.Model):
    quote_code = models.CharField(max_length=10)
    unique_link = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    xero_contact_id = models.UUIDField(default=None, null=True)
    xero_invoice_id = models.UUIDField(default=None, null=True)

    def __str__(self):
        return self.unique_link

