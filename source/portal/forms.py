from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from requests import RequestException

from country.models import Country
from .ebi_services import ebi_search_taxonomy_by_id, NoTaxonFoundException
from .models import EnvironmentalSampleType, HostSampleType


ALIQUOTTYPE_NAME_CHOICES = [
    ('DNA', 'DNA'),
    ('Strain', 'Strain'),
    ('EGS_Strain', 'EGS_Strain')
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

GMO_SAMPLES_CHOICES = [
    ('', 'Select a response'),
    ('Y', 'Yes'),
    ('N', 'No')
]


class EmailLinkForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254,
                             help_text="Please enter the email address "
                             "associated with your projects")


class UploadSampleSheetForm(forms.Form):
    file = forms.FileField(label="Upload sample sheet file")


class ProjectAcceptTermsForm(forms.Form):
    submission_requirements_name = forms.CharField(label="Full name")
    accepted = forms.BooleanField(
        required=True,
        label=("I declare that I have read and understood MicrobesNG sample submission requirements and that failure to"
               " follow them may result in my samples being disposed of appropriately."))
    gmo_samples = forms.ChoiceField(
        choices=GMO_SAMPLES_CHOICES,
        required=True,
        label="Are any of your samples genetically modified?"
    )


class ProjectEnaForm(forms.Form):
    ena_title = forms.CharField(label="Project title")
    ena_abstract = forms.CharField(widget=forms.Textarea, label="Project description (abstract)")


class ProjectAddCollaboratorForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()


class ProjectPermissionsForm(forms.Form):
    portal_login_required = forms.IntegerField(min_value=0, max_value=1)


class ProjectLineForm(forms.Form):
    customers_ref = forms.CharField(
        max_length=100,
        label="Your sample reference",
        help_text="e.g. MySample123",
        error_messages={
            'required': "'Customer's reference' (Sample name) is required.",
            'max_length': "'Customer's reference' (Sample name) cannot exceed"
                          " 100 characters."
        })
    aliquottype_name = forms.ChoiceField(
        choices=ALIQUOTTYPE_NAME_CHOICES,
        widget=forms.HiddenInput())
    taxon_id = forms.CharField(
        label="Sample Taxon Id (EBI/NCBI)",
        help_text="Start typing and choose the closest available",
        error_messages={
            'required': "'Taxon id' is required."
        })
    taxon_name = forms.CharField(
        label="Sample Taxon Name",
        required=False,
        disabled=True)
    volume_ul = forms.FloatField(
        required=False,
        min_value=30,
        label="Volume (µl)",
        error_messages={
            'min_value': "'Volume' greater than 30µl is required "
                         "for DNA samples."
        })
    dna_concentration_ng_ul = forms.FloatField(
        required=False,
        min_value=0.0,
        label="DNA concentration (ng/µl)",
        error_messages={
            'invalid': "'DNA concentration (ng/µl)' must be a number.",
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
            'required': "'Sample collection year' is required."
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
    host_taxon_id = forms.CharField(
        required=False,
        label="Host Taxon Id (EBI/NCBI)",
        help_text="Please enter the most specific taxon known then select the most appropriate",
        error_messages={
            'required': "'Host taxon id' is required."
        })
    host_taxon_name = forms.CharField(
        label="Host Taxon Name",
        required=False,
        disabled=True)
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
        taxon_id = cleaned_data.get('taxon_id')
        lab_experiment_type = cleaned_data.get('lab_experiment_type')
        host_taxon_id = cleaned_data.get('host_taxon_id')
        host_sample_type = cleaned_data.get('host_sample_type')
        environmental_sample_type = cleaned_data.get('environmental_sample_type')

        # EBI sample taxon id
        ebi_connection_error = ValidationError(
            _("We are temporarily unable to connect to the EBI to validate taxon ids. "
              " This may be due to a service outage. Please try again after a few minutes, or contact "
              " us if the problem persists."))
        try:
            ebi_response = ebi_search_taxonomy_by_id(taxon_id)
        except RequestException:
            non_field_errors.append(ebi_connection_error)
        except NoTaxonFoundException:
            self.add_error('taxon_id', ValidationError(
                _("Please enter a valid EBI/NCBI sample taxon id."),
                code='invalid'))
        else:
            cleaned_data['taxon_name'] = ebi_response[0]['fields']['name'][0]

        if dna_concentration_ng_ul:
            cleaned_data['dna_concentration_ng_ul'] = round(dna_concentration_ng_ul, 2)

        if volume_ul:
            cleaned_data['volume_ul'] = round(volume_ul, 2)

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
            if volume_ul is None:
                self.add_error('volume_ul', ValidationError(
                    _("'Volume (µl)' is required for DNA samples."),
                    code='required'))

            if dna_concentration_ng_ul is None:
                self.add_error('dna_concentration_ng_ul', ValidationError(
                    _("'DNA Concentration (ng/µl)' is required for DNA "
                      "samples."), code='required'))

        if study_type == 'Lab':
            if not lab_experiment_type:
                self.add_error('lab_experiment_type', ValidationError(
                    _("'Lab experiment type' is required when selecting"
                      " study type 'Lab'."), code='required'))
            if any(v for v in [host_taxon_id, host_sample_type, environmental_sample_type]):
                non_field_errors.append(
                    ValidationError(
                        _("Please only enter meta data for one study type"
                          " (lab, host or environmental)."))
                )

        if study_type == 'Host':
            if not host_sample_type:
                self.add_error('host_sample_type', ValidationError(
                    _("'Host sample type' is required when selecting"
                      " study type 'Host'."), code='required'))
            if any(v for v in [lab_experiment_type, environmental_sample_type]):
                non_field_errors.append(
                    ValidationError(
                        _("Please only enter meta data for one study type"
                          " (lab, host or environmental)."))
                )
            if host_taxon_id:
                try:
                    ebi_response = ebi_search_taxonomy_by_id(host_taxon_id)
                except RequestException:
                    non_field_errors.append(ebi_connection_error)
                except NoTaxonFoundException:
                    self.add_error(
                        'host_taxon_id',
                        ValidationError(_("Please enter a valid EBI/NCBI host taxon id."), code='invalid'))
                else:
                        cleaned_data['host_taxon_name'] = ebi_response[0]['fields']['name'][0]
            else:
                self.add_error('host_taxon_id', ValidationError(
                    _("'Host taxon id' is required when selecting"
                      " study type 'Host'."), code='required'))

        if study_type == 'Environmental':
            if not environmental_sample_type:
                self.add_error('environmental_sample_type', ValidationError(
                    _("'Environmental sample type' is required when selecting"
                      " study type 'Environmental'."), code='required'))
            if any(v for v in [host_taxon_id, host_sample_type, lab_experiment_type]):
                non_field_errors.append(
                    ValidationError(
                        _("Please only enter meta data for one study type"
                          " (lab, host or environmental)."))
                )

        if non_field_errors:
            raise ValidationError(non_field_errors)

        return cleaned_data
