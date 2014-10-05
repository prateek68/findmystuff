from django import forms

from models import AuthenticationToken 

class AddWebsiteForm(forms.ModelForm):
    """
    The form for adding a new new webapp and getting
    a authentication token
    """
    def __init__(self, user, *args, **kwargs):
        super(AddWebsiteForm, self).__init__(*args, **kwargs)

    class Meta:
        model   = AuthenticationToken
        fields  = ['website_name', 'website_url', 'website_IP']