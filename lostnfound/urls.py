from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from lostndfound import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^LnF404/', include('LnF404.urls')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^$', views.gmap,name='home'),
    url(r'^logout$', views.logout,name='logout'),
    url(r'^team/$', views.team,name='team'),
    url(r'^lostitem/$', views.lostitem, name='lostitem'),
    url(r'^founditem/$', views.founditem, name='founditem'),
    url(r'^history/$', views.history, name='history'),
    url(r'^log/$', views.log, name='log'),
    url(r'^found/(?P<found_id>\d+)/$', views.found, name='found'),
    url(r'^lost/(?P<lost_id>\d+)/$', views.lost, name='lost'),
    url(r'^reopenlost/(?P<lost_id>\d+)/$', views.reopenlost, name='reopenlost'),
    url(r'^reopenfound/(?P<found_id>\d+)/$', views.reopenfound, name='reopenfound'),
    url(r'', include('social.apps.django_app.urls',
        namespace='social')),
    url(r'^get_confirm_modal/(?P<itemtype>[a-z]+)/(?P<itemid>[0-9]+)/$',
     views.get_confirm_modal),
    url(r'^feedback/$', views.feedback, name='feedback'),
)

#TODO remove this. nginx will serve these.
urlpatterns += patterns('',
            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                    'document_root': settings.MEDIA_ROOT}))