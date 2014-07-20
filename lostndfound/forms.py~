from django.forms import ModelForm, Textarea, extras
from django import forms
from models import LostItem,FoundItem
from django.forms import ModelChoiceField
from django.contrib.admin import widgets

class LostItemForm(forms.ModelForm):
	#profilePhoto = forms.ImageField()
	class Meta:
		model = LostItem
	#dateOfBirth=forms.DateField(widget=extras.SelectDateWidget)
	#profilePhoto = forms.ImageField()
	itemname = forms.CharField(widget=forms.TextInput(attrs = {'class':'form-control','placeholder':'Object Lost'}))
	time = forms.DateField(widget=forms.DateInput(attrs = {'class':'form-control','placeholder':'Date'}))
	additonalinfo = forms.CharField(widget=forms.TextInput(attrs = {'class':'form-control','placeholder':'Additional Info'}))
	def __init__(self, *args, **kwargs):
		super(LostItemForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['readonly'] = True
		self.fields['firstname'].widget.attrs['readonly'] = True
		self.fields['lastname'].widget.attrs['readonly'] = True
		self.fields['status'].widget.attrs['readonly'] = True
		self.fields['email'].widget.attrs['readonly'] = True
		self.fields['pub_date'].widget.attrs['readonly'] = True
		self.fields['location'].empty_label = "Last Seen Location"
		self.fields['location'].widget.choices =self.fields['location'].choices
		#self.fields['mydatetime'].widget = widgets.AdminSplitDateTime()
		#self.fields['dateOfBirth'].widget = widgets.AdminDateWidget()
	time=forms.DateField(widget=forms.DateInput(attrs={'class':'timepicker'}))

class FoundItemForm(forms.ModelForm):
	#profilePhoto = forms.ImageField()
	class Meta:
		model = FoundItem
	#dateOfBirth=forms.DateField(widget=extras.SelectDateWidget)
	#profilePhoto = forms.ImageField()
	itemname = forms.CharField(widget=forms.TextInput(attrs = {'class':'form-control','placeholder':'Object Found'}))
	time = forms.DateField(widget=forms.DateInput(attrs = {'class':'form-control','placeholder':'Date'}))
	additonalinfo = forms.CharField(widget=forms.TextInput(attrs = {'class':'form-control','placeholder':'Additional Info'}))
	def __init__(self, *args, **kwargs):
		super(FoundItemForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['readonly'] = True
		self.fields['firstname'].widget.attrs['readonly'] = True
		self.fields['lastname'].widget.attrs['readonly'] = True
		self.fields['email'].widget.attrs['readonly'] = True
		self.fields['pub_date'].widget.attrs['readonly'] = True
		self.fields['status'].widget.attrs['readonly'] = True
		#self.fields['mydatetime'].widget = widgets.AdminSplitDateTime()
		#self.fields['dateOfBirth'].widget = widgets.AdminDateWidget()
	time=forms.DateField(widget=forms.DateInput(attrs={'class':'timepicker'}))
		
		
