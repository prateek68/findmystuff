from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

Location_Choices=(
('Boys Hostel','Boys Hostel'),
('Girls Hostel','Girls Hostel'),
('Academic Block','Academic Block'),
('Library Building','Library Building'),
('Student Activity Center','Student Activity Center'),
('Sports Field','Sports Field'),
('Faculty Residency','Faculty Residency'),
('Parking Area','Parking Area'),
)

Priority_Choices=(
(4,'Very Important'),
(3,'High'),
(2,'Medium'),
(1,'Low'),
)

class LostItem(models.Model):
	user 			= models.ForeignKey(User)
	itemname		= models.CharField(max_length=100)
	location 		= models.CharField(max_length=100, choices=Location_Choices)
	additionalinfo	= models.CharField(max_length=1000,null=True)
	priority 		= models.IntegerField(max_length=4,choices=Priority_Choices,null=True)
	status 			= models.BooleanField(max_length=100, default = True)
	time 			= models.DateField()
	pub_date 		= models.DateTimeField('date published', default=timezone.now)

class FoundItem(models.Model):
	user 			= models.ForeignKey(User)
	itemname		= models.CharField(max_length=100)
	location 		= models.CharField(max_length=100, choices=Location_Choices)
	status 			= models.BooleanField(default=True)
	additionalinfo 	= models.CharField(max_length=1000,null=True)
	priority 		= models.IntegerField(max_length=4,choices=Priority_Choices,null=True)
	time 			= models.DateField()
	pub_date 		= models.DateTimeField('date published', default=timezone.now)