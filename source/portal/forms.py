from django import forms


class EmailLinkForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254,
                             help_text="Please enter the email address "
                             "associated with your projects")


class ProjectLineForm(forms.Form):
    id = forms.CharField(disabled=True, widget=forms.HiddenInput())
    well_alpha = forms.CharField(disabled=True, required=False)
    sample_ref = forms.CharField(disabled=True, required=False)
    aliquottype_name = forms.CharField(disabled=True, required=False)
    customers_ref = forms.CharField(max_length=100)
    taxon_name = forms.CharField()
    queue_name = forms.CharField(disabled=True, required=False)
