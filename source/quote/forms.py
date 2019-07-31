from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from phonenumber_field.formfields import PhoneNumberField

from country.models import Country

FUNDING_TYPE_CHOICES = [
    ('', '---'),
    ('BBSRC funded', 'BBSRC funded'),
    ('Non-commercial', 'Other non-commercial (Academic/Charity)'),
    ('Industry', 'Industry'),
    ('Internal UoB', 'Internal, University of Birmingham')
]

REFERRAL_TYPE_CHOICES = [
    ('', '---'),
    ('SGM 2016', 'SGM Conference 2016'),
    ('Internal UoB', 'Internal UoB'),
    ('Word of mouth', 'Word of mouth'),
    ('Google', 'Google'),
    ('Twitter', 'Twitter'),
    ('Publication', 'Publication'),
    ('Other conference', 'Other conference')
]

BATCH_TYPE_CHOICES = [
    ('all together', 'Sending all samples together'),
    ('batches', 'Sending in multiple batches')
]

NAME_TITLE_CHOICES = [
    ('', ''),
    ('Dr', 'Dr'),
    ('Prof', 'Prof'),
    ('Mr', 'Mr'),
    ('Miss', 'Miss'),
    ('Ms', 'Ms'),
    ('Mrs', 'Mrs'),
    ('Mx', 'Mx'),
    ('Sir', 'Sir'),
    ('Lord', 'Lord')
]


class QuoteRequestForm(forms.Form):
    name_title = forms.ChoiceField(
        choices=NAME_TITLE_CHOICES,
        label=_("Title"),
        required=False)
    name_first = forms.CharField(max_length=50, label=_("First name"))
    name_last = forms.CharField(max_length=50, label=_("Last name"))
    email = forms.EmailField(label=_("Email address"))
    phone = PhoneNumberField(
        label=_("Phone number"),
        help_text=_("International customers: please enter a country code "
                    "e.g. +1-541-754-3010 for a US number."))
    primary_contact_is_pi = forms.BooleanField(
        label="Same as primary contact",
        required=False)
    pi_name_title = forms.ChoiceField(
        choices=NAME_TITLE_CHOICES,
        label=_("Title"),
        required=False)
    pi_name_first = forms.CharField(
        label=_("First name"),
        max_length=50,
        required=False)
    pi_name_last = forms.CharField(
        label=_("Last name"),
        max_length=50,
        required=False)
    pi_email = forms.EmailField(label=_("Email address"), required=False)
    organisation = forms.CharField(
        max_length=50,
        label=_("Institution / Company"))
    department = forms.CharField(max_length=50, required=False)
    street_line_1 = forms.CharField(
        max_length=50,
        label=_("Address lines"),
        widget=forms.TextInput(
            attrs={'placeholder': "e.g. Room W126, Biosciences building."}))
    street_line_2 = forms.CharField(
        max_length=50,
        label=_("Address line 2"),
        required=False)
    street_line_3 = forms.CharField(
        max_length=50,
        label=_("Address line 3"),
        required=False)
    city = forms.CharField(max_length=50)
    region = forms.CharField(
        max_length=50,
        label=_("Region / State"),
        required=False)
    postcode = forms.CharField(
        max_length=10,
        label=_("Postcode / Zip"),
        required=False)
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        to_field_name='name',
        widget=forms.TextInput(),
        error_messages={
            'required': "Sample collection country is required.",
            'invalid_choice': "Please select a valid country from the list."
        })
    funding_type = forms.ChoiceField(choices=FUNDING_TYPE_CHOICES)
    bbsrc_code = forms.CharField(required=False, label=_("BBSRC grant code"))
    is_confidential = forms.BooleanField(required=False)
    num_dna_samples = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        label=_("No. of DNA samples"))
    num_strain_samples = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        label=_("No. of strain samples"))
    num_enhanced_strain_samples = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        label=_("No. strains for enhanced sequencing"))
    confirm_strain_bsl2 = forms.BooleanField(
        required=False,
        label=_("Confirm your strains are BSL2 or lower"))
    confirm_enhanced_strain_bsl2 = forms.BooleanField(
        required=False,
        label=_("Confirm your enhanced strains are BSL2 or lower"))
    batch_type = forms.ChoiceField(
        choices=BATCH_TYPE_CHOICES,
        initial='all together')
    referral_type = forms.ChoiceField(
        choices=REFERRAL_TYPE_CHOICES,
        label=_("Where did you hear about us?"))
    comments = forms.CharField(required=False, widget=forms.Textarea())

    def clean(self):
        cleaned_data = super(QuoteRequestForm, self).clean()
        non_field_errors = []

        funding_type = cleaned_data.get('funding_type')
        bbsrc_code = cleaned_data.get('bbsrc_code')
        num_dna_samples = cleaned_data.get('num_dna_samples')
        num_strain_samples = cleaned_data.get('num_strain_samples')
        num_enhanced_strain_samples = cleaned_data.get("num_enhanced_strain_samples")
        confirm_strain_bsl2 = cleaned_data.get('confirm_strain_bsl2')
        confirm_enhanced_strain_bsl2 = cleaned_data.get('confirm_enhanced_strain_bsl2')
        primary_contact_is_pi = cleaned_data.get('primary_contact_is_pi')
        pi_name_title = cleaned_data.get('pi_name_title')
        pi_name_first = cleaned_data.get('pi_name_first')
        pi_name_last = cleaned_data.get('pi_name_last')
        pi_email = cleaned_data.get('pi_email')

        if num_strain_samples is None:
            num_strain_samples = 0
        if num_dna_samples is None:
            num_dna_samples = 0
        if num_enhanced_strain_samples is None:
            num_enhanced_strain_samples = 0

        if primary_contact_is_pi:
            cleaned_data['pi_name_title'] = ''
            cleaned_data['pi_name_first'] = ''
            cleaned_data['pi_name_last'] = ''
            cleaned_data['pi_email'] = ''
        else:
            if not pi_name_first:
                self.add_error(
                    'pi_name_first',
                    ValidationError(_("Principal investigator first name is required."),
                    code='required'))
            if not pi_name_last:
                self.add_error(
                    'pi_name_last',
                    ValidationError(_("Principal investigator last name is required."),
                    code='required'))
            if not pi_email:
                self.add_error(
                    'pi_email',
                    ValidationError(_("Principal investigator email is required."),
                    code='required'))

        if (funding_type == 'BBSRC funded' and not bbsrc_code):
            bbsrc_error = ValidationError(_("BBSRC code is required."))
            self.add_error('bbsrc_code', bbsrc_error)
            non_field_errors.append(bbsrc_error)

        if (num_strain_samples > 0 and not confirm_strain_bsl2):
            bsl2_error = ValidationError(
                _("You must confirm that any strains are BSL2 or below."))
            self.add_error('confirm_strain_bsl2', bsl2_error)
            non_field_errors.append(bsl2_error)

        if (num_enhanced_strain_samples > 0 and not confirm_enhanced_strain_bsl2):
            enhanced_bsl2_error = ValidationError(
                _("You must confirm that any strains for enhanced sequencing are BSL2 or below."))
            self.add_error('confirm_strain_bsl2', enhanced_bsl2_error)
            non_field_errors.append(enhanced_bsl2_error)

        if not (num_strain_samples or num_dna_samples or num_enhanced_strain_samples):
            non_field_errors.append(
                ValidationError(
                    _("A total sample quantity of at least one (strain or DNA)"
                      " is required."))
            )

        if non_field_errors:
            raise ValidationError(non_field_errors)

        return cleaned_data
