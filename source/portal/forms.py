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


class ProjectLineForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    customers_ref = forms.CharField(
        max_length=100,
        label="Your sample reference")
    taxon = forms.ModelChoiceField(
        queryset=Taxon.objects.filter(data_set__in=['Prokaryotes', 'Other']),
        to_field_name='name',
        widget=forms.TextInput(),
        label="Sample taxon",
        help_text="e.g. Escherichia coli (choose the closest available)")
    volume_ul = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        label="Volume (µl)")
    dna_concentration_ng_ul = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        label="DNA concentration (ng/µl)")
    geo_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        to_field_name='name',
        label="Sample collection country",
        widget=forms.TextInput())
    geo_specific_location = forms.CharField(
        max_length=100,
        label="Specific location",
        help_text="e.g. Royal Free Hospital, London")
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
        label="Study type")
    lab_experiment_type = forms.ChoiceField(
        choices=LAB_EXPERIMENT_TYPE,
        required=False,
        label="Experiment type")
    host_taxon = forms.ModelChoiceField(
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
