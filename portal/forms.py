from django import forms


class EmailLinkForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
