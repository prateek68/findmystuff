from django.dispatch import receiver
from django.db.models.signals import post_save
from lostndfound.models import Location
import lostndfound.Data as data

@receiver(post_save, sender=Location)
def update_locations(sender, **kwargs):
	Location_Choices = []
	limit = {}
	for location in Location.objects.all():
		Location_Choices.append((location.name, location.name))
		limit[location.name] = (location.x1, location.y1, location.x2, location.y2)

	if Location.objects.count == 0:
		Location_Choices = ("None", "None")
		limit["None"] = (0, 0, 90, 90)

	data.set_Location_Choices(tuple(Location_Choices))
	data.set_limit(limit)

update_locations(Location)
