from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from lostndfound.Data import get_Location_Choices

import string
from random import choice

Location_Choices=()

def generate_token():
	choices = string.letters + string.digits
	random_string = ''.join([choice(choices) for x in xrange(32)])
	return random_string

class LostItem(models.Model):
	user 			= models.ForeignKey(User)
	itemname		= models.CharField(max_length=100)
	location 		= models.CharField(max_length=100, choices=get_Location_Choices())
	additionalinfo	= models.CharField(max_length=1000,null=True)
	status 			= models.BooleanField(max_length=100, default = True)
	claimed			= models.BooleanField(default = False)
	time 			= models.DateField()
	pub_date 		= models.DateTimeField('date published', default=timezone.now)
	closing_token	= models.CharField(max_length=32)

	def __unicode__(self):
		return self.itemname
	def __repr__(self):
		return self.itemname

	def save(self, *args, **kwargs):
		self.closing_token = self.closing_token or generate_token()
		super(LostItem, self).save(*args, **kwargs)

class FoundItem(models.Model):
	user 			= models.ForeignKey(User)
	itemname		= models.CharField(max_length=100)
	location 		= models.CharField(max_length=100, choices=get_Location_Choices())
	status 			= models.BooleanField(default=True)
	additionalinfo 	= models.CharField(max_length=1000,null=True)
	claimed			= models.BooleanField(default = False)
	time 			= models.DateField()
	pub_date 		= models.DateTimeField('date published', default=timezone.now)
	closing_token	= models.CharField(max_length=32)

	def __unicode__(self):
		return self.itemname
	def __repr__(self):
		return self.itemname

	def save(self, *args, **kwargs):
		self.closing_token = self.closing_token or generate_token()
		super(FoundItem, self).save(*args, **kwargs)


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