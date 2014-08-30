from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from lostndfound.Data import get_Location_Choices

import string
from random import choice

Location_Choices=()

class LostItem(models.Model):
	user 			= models.ForeignKey(User)
	itemname		= models.CharField(max_length=100)
	location 		= models.CharField(max_length=100, choices=get_Location_Choices())
	additionalinfo	= models.CharField(max_length=1000,null=True)
	status 			= models.BooleanField(max_length=100, default = True)
	time 			= models.DateField()
	pub_date 		= models.DateTimeField('date published', default=timezone.now)
	found_by		= models.ForeignKey(User, related_name='foundby', null=True)
	image			= models.FileField(upload_to='images/')

	def __unicode__(self):
		return self.itemname
	def __repr__(self):
		return self.itemname

class FoundItem(models.Model):
	user 			= models.ForeignKey(User)
	itemname		= models.CharField(max_length=100)
	location 		= models.CharField(max_length=100, choices=get_Location_Choices())
	status 			= models.BooleanField(default=True)
	additionalinfo 	= models.CharField(max_length=1000,null=True)
	time 			= models.DateField()
	pub_date 		= models.DateTimeField('date published', default=timezone.now)
	lost_by			= models.ForeignKey(User, related_name='lostby', null=True)
	image			= models.FileField(upload_to='images/')

	def __unicode__(self):
		return self.itemname
	def __repr__(self):
		return self.itemname

class Location(models.Model):
	name			= models.CharField(max_length = 200)
	x1				= models.FloatField()
	y1				= models.FloatField()
	x2				= models.FloatField()
	y2				= models.FloatField()

	def __unicode__(self):
		return self.name
	def __repr__(self):
		return self.name