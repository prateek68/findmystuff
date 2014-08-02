from django.forms import ModelForm, Textarea, extras
from django import forms
from models import LostItem,FoundItem
from django.forms import ModelChoiceField
from django.contrib.admin import widgets

class LostItemForm(forms.ModelForm):
	class Meta:
		model  = LostItem
		fields = ['itemname', 'location',
				'additionalinfo', 'priority', 'time']

	def __init__(self, *args, **kwargs):
		super(LostItemForm, self).__init__(*args, **kwargs)
		self.fields['location'].empty_label = "Last Seen Location"
		self.fields['location'].widget.choices =self.fields['location'].choices

	itemname = forms.CharField(label = 'Item', widget=forms.TextInput(attrs = {
		'class':'form-control','placeholder':'Object Lost'}))
	time = forms.DateField(widget=forms.DateInput(attrs = {
		'class':'form-control','placeholder':'Date'}))
	additionalinfo = forms.CharField(label="Addition Information", widget=forms.TextInput(attrs = {
		'class':'form-control','placeholder':'Additional Info'}))

class FoundItemForm(forms.ModelForm):
	class Meta:
		model  = FoundItem
		fields = ['itemname', 'location',
				'additionalinfo', 'priority', 'time']

	def __init__(self, *args, **kwargs):
		super(FoundItemForm, self).__init__(*args, **kwargs)
		self.fields['location'].empty_label = "Found Location"
		self.fields['location'].widget.choices =self.fields['location'].choices

	itemname = forms.CharField(label="Item", widget=forms.TextInput(attrs = {
		'class':'form-control','placeholder':'Object Lost'}))
	time = forms.DateField(widget=forms.DateInput(attrs = {
		'class':'form-control','placeholder':'Date'}))
	additionalinfo = forms.CharField(label="Additional Info", widget=forms.TextInput(attrs = {
		'class':'form-control','placeholder':'Additional Info'}))
