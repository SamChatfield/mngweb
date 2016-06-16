from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from django import forms


FUNDING_TYPE_CHOICES = [
    ('BBSRC funded', 'BBSRC funded'),
    ('Non-commercial', 'Other non-commercial (Academic/Charity)'),
    ('Commercial', 'Commercial'),
    ('Internal UoB', 'Internal, University of Birmingham')
]

REFERRAL_TYPE_CHOICES = [
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


class QuoteRequestForm(forms.Form):
    name_title = forms.CharField(
        max_length=10, label=_("Title"),
        widget=forms.TextInput(attrs={'placeholder': "Dr"}))
    name_first = forms.CharField(
        max_length=50, label=_("First name"),
        widget=forms.TextInput(attrs={'placeholder': "John"}))
    name_last = forms.CharField(
        max_length=50, label=_("Last name"),
        widget=forms.TextInput(attrs={'placeholder': "Smith"}))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': "j.smith@bham.ac.uk"}))
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': "0121 4445555"}))
    organisation = forms.CharField(
        max_length=50, label=_("Organisation / Institution"),
        widget=forms.TextInput(
            attrs={'placeholder': "University of Birmingham"}))
    department = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(
            attrs={'placeholder': "Department of Biosciences"}))
    street_line_1 = forms.CharField(
        max_length=50, label=_("Address lines"),
        widget=forms.TextInput(
            attrs={'placeholder': "Room W126, Biosciences building"}))
    street_line_2 = forms.CharField(
        max_length=50, label=_("Address line 2"), required=False,
        widget=forms.TextInput(attrs={'placeholder': "Edgbaston"}))
    street_line_3 = forms.CharField(
        max_length=50, label=_("Address line 3"), required=False)
    city = forms.CharField(
        max_length=50, widget=forms.TextInput(
            attrs={'placeholder': "Birmingham"}))
    region = forms.CharField(
        max_length=50, label=_("Region / State"), help_text=_("Optional"),
        required=False, widget=forms.TextInput(
            attrs={'placeholder': "West Midlands"}))
    postcode = forms.CharField(
        max_length=10, label=_("Postcode / Zip"), required=False,
        widget=forms.TextInput(attrs={'placeholder': "B15 2TT"}))
    country = forms.CharField(
        max_length=30, widget=forms.TextInput(
            attrs={'placeholder': "United Kingdom"}))
    funding_type = forms.ChoiceField(choices=FUNDING_TYPE_CHOICES)
    bbsrc_code = forms.CharField(
        required=False, label=_("BBSRC grant code"),
        widget=forms.TextInput(attrs={'placeholder': "BB/M0101234/1"}))
    is_confidential = forms.BooleanField(required=False)
    num_dna_samples = forms.IntegerField(
        min_value=0, initial=0, label=_("No. of DNA samples"))
    num_strain_samples = forms.IntegerField(
        min_value=0, initial=0, label=_("No. of strain samples"))
    confirm_strain_bsl2 = forms.BooleanField(
        required=False, label=_("Confirm your strains are BSL2 or lower"))
    batch_type = forms.ChoiceField(
        choices=BATCH_TYPE_CHOICES, initial='all together')
    referral_type = forms.ChoiceField(
        choices=REFERRAL_TYPE_CHOICES, label=_("Where did you hear about us?"))
    comments = forms.CharField(required=False, widget=forms.Textarea())

    def clean(self):
        if (self.cleaned_data.get('funding_type') == 'BBSRC funded' and
                not self.cleaned_data.get('bbsrc_code')):

            self.add_error(
                'bbsrc_code',
                ValidationError(_("BBSRC code is required"), code='required')
            )

        if (self.cleaned_data.get('num_strain_samples') > 0 and
                not self.cleaned_data.get('confirm_strain_bsl2')):

            self.add_error(
                'confirm_strain_bsl2',
                ValidationError(_(
                    "You must confirm strains are BSL2 or below"),
                    code='required')
            )

        if (self.cleaned_data.get('num_strain_samples') < 1 and
                self.cleaned_data.get('num_dna_samples') < 1):

            raise ValidationError(
                _("A total sample quantity of at least one (strain or DNA) is required"),
                code='required')

        return self.cleaned_data
