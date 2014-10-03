from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from lostndfound import startup
from lostndfound.views import handle404

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^LnF404/', include('LnF404.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^', include('lostndfound.urls')),
)

#TODO remove this. nginx will serve these.
urlpatterns += patterns('',
            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                    'document_root': settings.MEDIA_ROOT}))

handler404 = handler500 = handle404

startup.startup_cache()