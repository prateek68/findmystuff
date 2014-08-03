from django.contrib import admin
from lostndfound.models import LostItem, FoundItem, Location

admin.site.register(LostItem)
admin.site.register(FoundItem)
admin.site.register(Location)