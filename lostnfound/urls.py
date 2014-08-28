from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin


PATH = getattr(settings, 'URL_PATH', '')

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^LnF404/', include('LnF404.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^%s$' % PATH, 'lostndfound.views.home',name='home'),
    url(r'^%slogout$' % PATH, 'lostndfound.views.logout',name='logout'),
    url(r'^%steam/$' % PATH, 'lostndfound.views.team',name='team'),
    url(r'^%sdone/$' % PATH, 'lostndfound.views.done', name='done'),
    url(r'^%slostitem/$' % PATH, 'lostndfound.views.lostitem', name='lostitem'),
    url(r'^%sfounditem/$' % PATH, 'lostndfound.views.founditem', name='founditem'),
    url(r'^%sgmap/$' % PATH, 'lostndfound.views.gmap', name='gmap'),
    url(r'^%shistory/$' % PATH, 'lostndfound.views.history', name='history'),
    url(r'^%slog/$' % PATH, 'lostndfound.views.log', name='log'),
    url(r'^found/(?P<found_id>\d+)/$', 'lostndfound.views.found', name='found'),
    url(r'^lost/(?P<lost_id>\d+)/$', 'lostndfound.views.lost', name='lost'),
    url(r'^reopenlost/(?P<lost_id>\d+)/$', 'lostndfound.views.reopenlost', name='reopenlost'),
    url(r'^reopenfound/(?P<found_id>\d+)/$', 'lostndfound.views.reopenfound', name='reopenfound'),
    url(r'%s' % PATH, include('social.apps.django_app.urls',
        namespace='social')),
    url(r'^complete/(?P<itemtype>[a-z]+)/(?P<itemid>\d+)/(?P<token>[a-zA-Z0-9]+)/$', 'lostndfound.views.close_item',
        name="close_item"),
)
