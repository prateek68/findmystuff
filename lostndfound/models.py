from django.db import models
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

	username= models.CharField(max_length=100)
	firstname= models.CharField(max_length=100)
	lastname=models.CharField(max_length=100)
	
	email = models.EmailField(max_length=75)
	itemname=models.CharField(max_length=100)
	location=models.CharField(max_length=100, choices=Location_Choices)
	#profilePhoto = models.ImageField(blank = True, null = True,upload_to = 'images/', max_length = 255)
	additonalinfo=models.CharField(max_length=1000,null=True)
	priority=models.IntegerField(max_length=4,choices=Priority_Choices,null=True)
	status=models.CharField(max_length=100)
	time=models.DateField()
	pub_date = models.DateTimeField('date published')

class FoundItem(models.Model):

	username= models.CharField(max_length=100)
	firstname= models.CharField(max_length=100)
	lastname=models.CharField(max_length=100)
	
	email = models.EmailField(max_length=75)
	itemname=models.CharField(max_length=100)
	location=models.CharField(max_length=100, choices=Location_Choices)
	status=models.CharField(max_length=100)
	#profilePhoto = models.ImageField(blank = True, null = True,upload_to = 'images/', max_length = 255)
	additonalinfo=models.CharField(max_length=1000,null=True)
	priority=models.IntegerField(max_length=4,choices=Priority_Choices,null=True)
	time=models.DateField()
	pub_date = models.DateTimeField('date published')
	

