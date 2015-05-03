from django.conf import settings
from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
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
    url(r'^get_confirm_modal/(?P<itemtype>[a-z]+)/(?P<itemid>[0-9]+)/$',
     views.get_confirm_modal),
    url(r'^feedback/$', views.feedback, name='feedback'),
    url(r'^delete/lost/(?P<lost_id>\d+)/$', views.deletelost, name='deletelost'),
    url(r'^delete/found/(?P<found_id>\d+)/$', views.deletefound, name='deletefound'),
    url(r'^search/$', views.search, name = 'search'),

    # FB developer policy
    url(r'^fb/policy/$', views.fb_privacy_policy, name='fb_privacy_policy'),
    url(r'^fb/login/$', views.fb_login, name='fb_login'),
)