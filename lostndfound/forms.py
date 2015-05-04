from datetime import date

from django import forms
from django.contrib.admin import widgets
from django.forms import ModelChoiceField
from django.forms import ModelForm, Textarea

from models import LostItem,FoundItem, Feedback
from lostndfound.cached import get_location_choices

def validate_date(value):
    """validates the date. It should not be more than today."""
    from django.core.exceptions import ValidationError
    if date.today() < value:
        raise ValidationError("Date not passed")
    return True

class LostItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LostItemForm, self).__init__(*args, **kwargs)
        self.fields['location'] = forms.ChoiceField(choices=list(get_location_choices()))
        self.fields['location'].empty_label = "Last Seen Location"
        self.fields['image'].required = False

    itemname = forms.CharField(label = 'Item', widget=forms.TextInput(attrs = {
        'class':'form-control','placeholder':'Object Lost', 'id': "item_name_field"}))
    time = forms.DateField(label = 'Last seen on', widget=forms.DateInput(attrs = {
        'class':'form-control','placeholder':'Date'}), validators = [validate_date])
    additionalinfo = forms.CharField(label="More Details", widget=forms.Textarea(attrs = {
        'class':'form-control','placeholder':'Describe the item you lost explicitly.'}))

    class Meta:
        model  = LostItem
        fields = ['itemname', 'location',
                'additionalinfo', 'time', 'time_of_day', 'image']

class FoundItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FoundItemForm, self).__init__(*args, **kwargs)
        self.fields['location'].empty_label = "Found Location"
        self.fields['location'] = forms.ChoiceField(choices=list(get_location_choices()))
        self.fields['image'].required = False

    itemname = forms.CharField(label="Item", widget=forms.TextInput(attrs = {
        'class':'form-control','placeholder':'Object Found', 'id': "item_name_field"}))
    time = forms.DateField(label='Found on', widget=forms.DateInput(attrs = {
        'class':'form-control','placeholder':'Date'}), validators = [validate_date])
    additionalinfo = forms.CharField(label="More Details", widget=forms.Textarea(attrs = {
        'class':'form-control','placeholder':'Describe the item you found explicitly.'}))

    class Meta:
        model  = FoundItem
        fields = ['itemname', 'location',
                'additionalinfo', 'time', 'image']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model   = Feedback
        fields  = ['feedback']
