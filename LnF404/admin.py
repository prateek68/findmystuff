from django.contrib import admin
from LnF404.models import AuthenticationToken, RecentLostItem

admin.site.register(AuthenticationToken)
admin.site.register(RecentLostItem)
