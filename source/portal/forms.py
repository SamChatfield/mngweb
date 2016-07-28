from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from country.models import Country
from taxon.models import Taxon

from .models import EnvironmentalSampleType, HostSampleType

ALIQUOTTYPE_NAME_CHOICES = [
    ('DNA', 'DNA'),
    ('Strain', 'Strain')
]

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
    ('', '---'),
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
    customers_ref = forms.CharField(
        max_length=100,
        label="Your sample reference",
        error_messages={
            'required': "'Customer's reference' (Sample name) is required.",
            'max_length': "'Customer's reference' (Sample name) cannot exceed"
                          " 100 characters."
        })
    aliquottype_name = forms.ChoiceField(
        choices=ALIQUOTTYPE_NAME_CHOICES,
        widget=forms.HiddenInput())
    taxon_name = forms.ModelChoiceField(
        queryset=Taxon.objects.filter(data_set__in=['Prokaryotes', 'Other']),
        to_field_name='name',
        widget=forms.TextInput(),
        label="Sample taxon",
        help_text="e.g. Escherichia coli (choose the closest available)",
        error_messages={
            'required': "'Taxon' is required.",
            'invalid_choice': "Please select a valid 'taxon' from the list."
        })
    volume_ul = forms.DecimalField(
        required=False,
        min_value=30,
        max_value=100,
        decimal_places=2,
        label="Volume (µl)",
        error_messages={
            'max_decimal_places': "Volume (µl) should have a maximum of 2 "
                                  "decimal places.",
            'min_value': "A 'volume' within the range 30-100µl is required "
                         "for DNA samples.",
            'max_value': "A 'volume' within the range 30-100µl is required "
                         "for DNA samples.",
            'invalid': "A 'volume' within the range 30-100µl is required "
                         "for DNA samples.",
        })
    dna_concentration_ng_ul = forms.DecimalField(
        required=False,
        min_value=1,
        max_value=30,
        decimal_places=2,
        label="DNA concentration (ng/µl)",
        error_messages={
            'max_decimal_places': "'DNA Concentration (ng/µl)'' should have "
                                  "a maximum of 2 decimal places.",
            'min_value': "A 'DNA Concentration' within the range 1-30ng/µl is "
                         "required for DNA samples.",
            'max_value': "A 'DNA Concentration' within the range 1-30ng/µl is "
                         "required for DNA samples.",
            'invalid': "'DNA concentration (ng/µl)' must be a number (max. 2 "
                       "decimal places).",
        })
    geo_country_name = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        to_field_name='name',
        label="Sample collection country",
        widget=forms.TextInput(),
        error_messages={
            'required': "'Sample collection country' is required.",
            'invalid_choice': "Please select a valid 'sample collection "
                              "country' from the list."
        })
    geo_specific_location = forms.CharField(
        label="Specific location",
        help_text="e.g. Royal Free Hospital, London",
        error_messages={
            'required': "'Sample collection specific location' is required."
        })
    collection_day = forms.IntegerField(
        min_value=1,
        max_value=31,
        required=False,
        label="Day",
        help_text="Day",
        error_messages={
            'invalid': "Please enter a 'Sample collection day' between 1 and "
                       "31 (leave blank if unknown).",
            'min_value': "Please enter a 'Sample collection day' between 1 "
                         "and 31 (leave blank if unknown).",
            'max_value': "Please enter a 'Sample collection day' between 1 "
                         "and 31 (leave blank if unknown).",
        })
    collection_month = forms.TypedChoiceField(
        coerce=int,
        choices=MONTH_CHOICES,
        required=False,
        label="Month",
        help_text="Month",
        error_messages={
            'invalid_choice': "Please select a valid 'Sample collection "
                              "month' (leave blank if unknown)."
        })
    collection_year = forms.IntegerField(
        min_value=1800,
        max_value=datetime.now().year,
        label="Year",
        help_text="Year",
        error_messages={
            'min_value': "Please enter a 'Sample collection year' between "
                         "1800 and the current year (leave blank if unknown).",
            'max_value': "Please enter a 'Sample collection year' between "
                         "1800 and the current year (leave blank if unknown).",
            'invalid': "Please enter a 'Sample collection year' between 1800 "
                       "and the current year (leave blank if unknown).",
        })
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
        help_text="Further details about your sample",
        error_messages={
            'required': "'Further details' is a required field.",
        })

    def clean(self):
        cleaned_data = super(ProjectLineForm, self).clean()
        non_field_errors = []

        collection_year = cleaned_data.get('collection_year')
        collection_month = cleaned_data.get('collection_month')
        collection_day = cleaned_data.get('collection_day')
        aliquottype_name = cleaned_data.pop('aliquottype_name')  # pop!
        volume_ul = cleaned_data.get('volume_ul')
        dna_concentration_ng_ul = cleaned_data.get('dna_concentration_ng_ul')
        study_type = cleaned_data.get('study_type')
        lab_experiment_type = cleaned_data.get('lab_experiment_type')
        host_taxon_name = cleaned_data.get('host_taxon_name')
        host_sample_type = cleaned_data.get('host_sample_type')
        environmental_sample_type = cleaned_data.get('environmental_sample_type')

        if collection_year and collection_month and collection_day:
            try:
                datetime(
                    year=collection_year,
                    month=collection_month,
                    day=collection_day)
            except ValueError:
                non_field_errors.append(
                    ValidationError(
                        _("The sample collection day, month and year entered"
                          " do not represent a valid date."))
                )

        if aliquottype_name == 'DNA':
            if not volume_ul:
                self.add_error('volume_ul', ValidationError(
                    _("'Volume (µl)' is required for DNA samples."),
                    code='required'))

            if not dna_concentration_ng_ul:
                self.add_error('dna_concentration_ng_ul', ValidationError(
                    _("'DNA Concentration (ng/µl)' is required for DNA "
                      "samples."), code='required'))

        if study_type == 'Lab':
            if not lab_experiment_type:
                self.add_error('lab_experiment_type', ValidationError(
                    _("'Lab experiment type' is required when selecting"
                      " study type 'Lab'."), code='required'))
            if (host_taxon_name or host_sample_type or environmental_sample_type):
                non_field_errors.append(
                    ValidationError(
                        _("Please only enter meta data for one study type"
                          " (lab, host or environmental)."))
                )

        if study_type == 'Host':
            if not host_taxon_name:
                self.add_error('host_taxon_name', ValidationError(
                    _("'Host taxon name' is required when selecting"
                      " study type 'Host'."), code='required'))
            if not host_sample_type:
                self.add_error('host_sample_type', ValidationError(
                    _("'Host sample type' is required when selecting"
                      " study type 'Host'."), code='required'))
            if (lab_experiment_type or environmental_sample_type):
                non_field_errors.append(
                    ValidationError(
                        _("Please only enter meta data for one study type"
                          " (lab, host or environmental)."))
                )

        if study_type == 'Environmental':
            if not environmental_sample_type:
                self.add_error('environmental_sample_type', ValidationError(
                    _("'Environmental sample type' is required when selecting"
                      " study type 'Environmental'."), code='required'))
            if (host_taxon_name or host_sample_type or lab_experiment_type):
                non_field_errors.append(
                    ValidationError(
                        _("Please only enter meta data for one study type"
                          " (lab, host or environmental)."))
                )

        if non_field_errors:
            raise ValidationError(non_field_errors)

        return cleaned_data
