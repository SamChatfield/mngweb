from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from country.models import Country
from requests import RequestException

class QuoteForm(forms.Form):
    quote_code = forms.CharField(label='Quote code', max_length=10,
                             help_text="Please enter the quote code, eg. QT12345")

class ConfirmOrderForm(forms.Form):
    unique_reference_id = forms.CharField(label='Your reference', max_length=100,
                             help_text='Please enter your unique reference ID, e.g. PO number for the invoice')

    name_first = forms.CharField(label='First name', max_length=50)
    name_last = forms.CharField(label='Last name', max_length=50)
    organisation = forms.CharField(label='Organisation', max_length=100)
    email = forms.CharField(label='Email', max_length=50, help_text="Billing contact email")
    department = forms.CharField(label='Department', max_length=50, required=False)
    street_line_one = forms.CharField(label='Street Line 1', max_length=100, help_text="First line of street address")
    street_line_two = forms.CharField(label='Street Line 2', max_length=100, help_text="Second line of street address", required=False)
    street_line_three = forms.CharField(label='Street Line 3', max_length=100, help_text="Third line of street address", required=False)
    city = forms.CharField(label='City', max_length=50, help_text="Town or city")
    region = forms.CharField(label='Region', max_length=50, help_text="Region", required=False)
    postcode = forms.CharField(label='Postal code', max_length=50, help_text="Postcode")
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        to_field_name='iso2',
        label="collection country",
        error_messages={
            'required': "'Country' is required.",
            'invalid_choice': "Please select a valid 'sample collection "
                              "country' from the list."
        })


    def populate_form(self, conversion_table, input):
        for key, val in conversion_table.items():
             self.fields[key].initial = input[val]
