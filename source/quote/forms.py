from django import forms


FUNDING_TYPE_CHOICES = [
    ('BBSRC funded', 'BBSRC funded'),
    ('Non-commercial', 'Non-commercial'),
    ('Commercial', 'Commercial'),
    ('Internal UoB', 'Internal (University of Birmingham)')
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
        max_length=10, label="Title",
        widget=forms.TextInput(attrs={'placeholder': "Dr"})
    )
    name_first = forms.CharField(
        max_length=50, label="First name",
        widget=forms.TextInput(attrs={'placeholder': "John"})
    )
    name_last = forms.CharField(
        max_length=50, label="Last name",
        widget=forms.TextInput(attrs={'placeholder': "Smith"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': "j.smith@bham.ac.uk"})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': "0121 4445555"})
    )
    organisation = forms.CharField(
        max_length=50, label="Organisation / Institution",
        widget=forms.TextInput(attrs={'placeholder': "University of Birmingham"})
    )
    department = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': "Department of Biosciences"})
    )
    street_line_1 = forms.CharField(
        max_length=50, label="Address lines",
        widget=forms.TextInput(attrs={'placeholder': "Room W126, Biosciences building"})
    )
    street_line_2 = forms.CharField(
        max_length=50, label="Address line 2",
        widget=forms.TextInput(attrs={'placeholder': "Edgbaston"})
    )
    street_line_3 = forms.CharField(max_length=50, label="Address line 3")
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': "Birmingham"})
    )
    region = forms.CharField(
        max_length=50, label="Region / State", help_text="Optional",
        widget=forms.TextInput(attrs={'placeholder': "West Midlands"})
    )
    postcode = forms.CharField(
        max_length=10, label="Postcode / Zip",
        widget=forms.TextInput(attrs={'placeholder': "B15 2TT"})
    )
    country = forms.CharField(max_length=30)
    funding_type = forms.ChoiceField(choices=FUNDING_TYPE_CHOICES)
    is_confidential = forms.BooleanField(required=False)
    num_dna_samples = forms.IntegerField(
        min_value=0, initial=0,
        label="No. of DNA samples"
    )
    num_strain_samples = forms.IntegerField(
        min_value=0, initial=0,
        label="No. of strain samples"
    )
    confirm_strain_bsl2 = forms.BooleanField(
        required=False, label="Confirm your strains are BSL2 or lower")
    batch_type = forms.ChoiceField(choices=BATCH_TYPE_CHOICES, initial='all together')
    referral_type = forms.ChoiceField(
        choices=REFERRAL_TYPE_CHOICES, label="Where did you hear about us?")
    comments = forms.CharField(required=False, widget=forms.Textarea())
