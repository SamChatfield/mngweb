from datetime import datetime

from django import forms


ISOLATE_TYPE_CHOICES = [
    ('', ''),
    ('lab', 'Lab'),
    ('host', 'Host'),
    ('environmental', 'Environmental')
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
    'Gene knockout',
    'Gene knockin',
    'Selection experiment',
    'Site-directed mutagenesis',
    'Other'
]


class EmailLinkForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254,
                             help_text="Please enter the email address "
                             "associated with your projects")


class ProjectLineForm(forms.Form):
    id = forms.CharField(disabled=True, widget=forms.HiddenInput())
    customers_ref = forms.CharField(
        max_length=100, label="Your Reference",
        widget=forms.TextInput(attrs={'placeholder': 'MySample123'})
    )
    taxon_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Escherichia coli'}))
    volume_ul = forms.DecimalField(
        min_value=0, decimal_places=2, label="Volume (µl)")
    dna_concentration_ng_ul = forms.DecimalField(
        min_value=0, decimal_places=2, label="DNA concentration (ng/µl)")
    geo_country_name = forms.CharField(
        max_length=100, label="Country of sample collection",
        widget=forms.TextInput(attrs={'placeholder': 'United Kingdom'})
    )
    geo_specific_location = forms.CharField(
        max_length=100, label="Specific location",
        widget=forms.TextInput(
            attrs={'placeholder': 'Royal Free Hospital, London'})
    )
    collection_day = forms.IntegerField(
        label="Day", min_value=1, max_value=31, required=False,
        widget=forms.NumberInput(attrs={'placeholder': "31"})
    )
    collection_month = forms.TypedChoiceField(
        coerce=int, label="Month", choices=MONTH_CHOICES, required=False
    )
    collection_year = forms.IntegerField(
        label="Year", min_value=1900, max_value=datetime.now().year,
        widget=forms.NumberInput(attrs={'placeholder': "2014"})
    )
    isolate_type = forms.ChoiceField(
        label="Isolate type", choices=ISOLATE_TYPE_CHOICES,
    )
    lab_experiment_type = forms.ChoiceField(
        label="Experiment type", choices=LAB_EXPERIMENT_TYPE
    )
    host_taxon_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Homo sapiens'}))
