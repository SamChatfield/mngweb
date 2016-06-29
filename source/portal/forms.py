from datetime import datetime

from django import forms

from .models import EnvironmentalSampleType, HostSampleType
from country.models import Country
from taxon.models import Taxon


ISOLATE_TYPE_CHOICES = [
    ('', ''),
    ('Lab', 'Lab'),
    ('Host', 'Host'),
    ('Environmental', 'Environmental')
]

MONTH_CHOICES = (
    ('', '---'),
    (1, 'JAN'),
    (2, 'FEB'),
    (3, 'MAR'),
    (4, 'APR'),
    (5, 'MAY'),
    (6, 'JUN'),
    (7, 'JUL'),
    (8, 'AUG'),
    (9, 'SEP'),
    (10, 'OCT'),
    (11, 'NOV'),
    (12, 'DEC')
)

LAB_EXPERIMENT_TYPE = [
    ('Gene Knockout', 'Gene Knockout'),
    ('Gene Knockin', 'Gene Knockin'),
    ('Selection Experiment', 'Selection Experiment'),
    ('Site-directed mutagenesis', 'Site-directed mutagenesis'),
    ('Other', 'Other'),
]


class EmailLinkForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254,
                             help_text="Please enter the email address "
                             "associated with your projects")


class UploadSampleSheetForm(forms.Form):
    file = forms.FileField(label="Upload sample sheet file")


class ProjectLineForm(forms.Form):
    sample_ref = forms.CharField(widget=forms.HiddenInput())
    customers_ref = forms.CharField(
        max_length=100,
        label="Your sample reference",
        error_messages={
            'required': "Customer's reference (Sample name) is required.",
            'max_length': "Customer's reference (Sample name) cannot exceep 100 characters."
        })
    taxon_name = forms.ModelChoiceField(
        queryset=Taxon.objects.filter(data_set__in=['Prokaryotes', 'Other']),
        to_field_name='name',
        widget=forms.TextInput(),
        label="Sample taxon",
        help_text="e.g. Escherichia coli (choose the closest available)",
        error_messages={
            'required': "Taxon is required.",
            'invalid_choice': "Please select a valid taxon from the list."
        })
    volume_ul = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        required=False,
        label="Volume (µl)",
        error_messages={
            'max_decimal_places': "Volume (µl) should have a maximum of 2 decimal places."
        })
    dna_concentration_ng_ul = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        required=False,
        label="DNA concentration (ng/µl)",
        error_messages={
            'max_decimal_places': "DNA Concentration (ng/µl) should have a maximum of 2 decimal places."
        })
    geo_country_name = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        to_field_name='name',
        label="Sample collection country",
        widget=forms.TextInput(),
        error_messages={
            'required': "Sample collection country is required.",
            'invalid_choice': "Please select a valid sample collection country from the list."
        })
    geo_specific_location = forms.CharField(
        label="Specific location",
        help_text="e.g. Royal Free Hospital, London",
        error_messages={
            'required': "Sample collection specific location is required."
        })
    collection_day = forms.IntegerField(
        min_value=1,
        max_value=31,
        required=False,
        label="Day",
        help_text="Day")
    collection_month = forms.TypedChoiceField(
        coerce=int,
        choices=MONTH_CHOICES,
        required=False,
        label="Month",
        help_text="Month")
    collection_year = forms.IntegerField(
        min_value=1900,
        max_value=datetime.now().year,
        label="Year",
        help_text="Year")
    study_type = forms.ChoiceField(
        choices=ISOLATE_TYPE_CHOICES,
        label="Study type",
        help_text="Is your strain lab derived, sampled from a host or sampled"
        " from the environment?")
    lab_experiment_type = forms.ChoiceField(
        choices=LAB_EXPERIMENT_TYPE,
        required=False,
        label="Experiment type")
    host_taxon_name = forms.ModelChoiceField(
        required=False,
        queryset=Taxon.objects.all(),
        to_field_name='name',
        widget=forms.TextInput(),
        help_text="e.g. Homo sapiens")
    host_sample_type = forms.ModelChoiceField(
        required=False,
        queryset=HostSampleType.objects.all(),
        to_field_name='name',
        widget=forms.TextInput(),
        help_text="e.g. Stool")
    environmental_sample_type = forms.ModelChoiceField(
        required=False,
        queryset=EnvironmentalSampleType.objects.all(),
        to_field_name='name',
        widget=forms.TextInput(),
        help_text="e.g. Soil")
    further_details = forms.CharField(
        required=False,
        help_text="Further details about your sample")
