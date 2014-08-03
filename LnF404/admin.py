from django.contrib import admin
from LnF404.models import AuthenticationTokens, RecentLostItems

admin.site.register(AuthenticationTokens)
admin.site.register(RecentLostItems)
# Register your models here.