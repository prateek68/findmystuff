from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from cached import get_location_choices

time_of_day_choices = (('XXX', 'Don\'t know'),
                        ('MNG', 'Morning'),
                        ('AFT', 'Afternoon'),
                        ('EVE', 'Evening'),
                        ('NGT', 'Night'),
                        )

class LostItem(models.Model):
    user            = models.ForeignKey(User)
    itemname        = models.CharField(max_length=100)
    location        = models.CharField(max_length=100,
                        choices=get_location_choices())
    additionalinfo  = models.CharField(max_length=1000,null=True)
    status          = models.BooleanField(max_length=100, default = True)
    time            = models.DateField()
    pub_date        = models.DateTimeField('date published',
                        default=timezone.now)
    found_by        = models.ForeignKey(User,
                        related_name='foundby', null=True)
    image           = models.FileField(upload_to='images/')
    time_of_day     = models.CharField(max_length=3,
                        choices=time_of_day_choices, default='XXX')

    def __repr__(self):
        return self.itemname

class FoundItem(models.Model):
    user            = models.ForeignKey(User)
    itemname        = models.CharField(max_length=100)
    location        = models.CharField(max_length=100,
                        choices=get_location_choices())
    status          = models.BooleanField(default=True)
    additionalinfo  = models.CharField(max_length=1000,null=True)
    time            = models.DateField()
    pub_date        = models.DateTimeField('date published',
                        default=timezone.now)
    lost_by         = models.ForeignKey(User,
                        related_name='lostby', null=True)
    image           = models.FileField(upload_to='images/')

    def __repr__(self):
        return self.itemname

class Location(models.Model):
    name            = models.CharField(max_length = 200)
    x1              = models.FloatField()
    y1              = models.FloatField()
    x2              = models.FloatField()
    y2              = models.FloatField()

    def __unicode__(self):
        return self.name
    def __repr__(self):
        return self.name

class Feedback(models.Model):
    user            = models.ForeignKey(User)
    feedback        = models.TextField(max_length=500)
    date            = models.DateTimeField(default=timezone.now)
    fixed           = models.BooleanField(default=False)

    def __repr__(self):
        return self.feedback
