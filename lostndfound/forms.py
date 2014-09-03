from django.forms import ModelForm, Textarea, extras
from django import forms
from models import LostItem,FoundItem, Feedback
from django.forms import ModelChoiceField
from django.contrib.admin import widgets
from datetime import date
from lostndfound.Data import get_Location_Choices

def validate_date(value):
	from django.core.exceptions import ValidationError
	if date.today() < value:
		raise ValidationError("Date not passed")
	return True

class LostItemForm(forms.ModelForm):
	class Meta:
		model  = LostItem
		fields = ['itemname', 'location',
				'additionalinfo', 'time', 'image']

	def __init__(self, *args, **kwargs):
		super(LostItemForm, self).__init__(*args, **kwargs)
		self.fields['location'] = forms.ChoiceField(choices=list(get_Location_Choices()))
		self.fields['location'].empty_label = "Last Seen Location"
		self.fields['image'].required = False

	itemname = forms.CharField(label = 'Item', widget=forms.TextInput(attrs = {
		'class':'form-control','placeholder':'Object Lost'}))
	time = forms.DateField(label = 'Last seen on', widget=forms.DateInput(attrs = {
		'class':'form-control','placeholder':'Date'}), validators = [validate_date])
	additionalinfo = forms.CharField(label="More Details", widget=forms.Textarea(attrs = {
		'class':'form-control','placeholder':'Describe the item you lost explicitly.'}))

class FoundItemForm(forms.ModelForm):
	class Meta:
		model  = FoundItem
		fields = ['itemname', 'location',
				'additionalinfo', 'time', 'image']

	def __init__(self, *args, **kwargs):
		super(FoundItemForm, self).__init__(*args, **kwargs)
		self.fields['location'].empty_label = "Found Location"
		self.fields['location'] = forms.ChoiceField(choices=list(get_Location_Choices()))
		self.fields['image'].required = False


	itemname = forms.CharField(label="Item", widget=forms.TextInput(attrs = {
		'class':'form-control','placeholder':'Object Found'}))
	time = forms.DateField(label='Found on', widget=forms.DateInput(attrs = {
		'class':'form-control','placeholder':'Date'}), validators = [validate_date])
	additionalinfo = forms.CharField(label="More Details", widget=forms.Textarea(attrs = {
		'class':'form-control','placeholder':'Describe the item you found explicitly.'}))

class FeedbackForm(forms.ModelForm):
	class Meta:
		model 	= Feedback
		fields 	= ['feedback']
