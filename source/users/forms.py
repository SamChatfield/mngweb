from django import forms

class CustomSignupForm(forms.Form):
    """Defines 'extra' fields to extend the allauth signup form"""
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
