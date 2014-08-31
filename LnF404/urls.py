from django.conf.urls import patterns, url
from LnF404 import views

urlpatterns = patterns('',
	url(r'^add/$',views.add, name='add_404_website'),
	url(r'^refresh/(?P<token_id>[0-9]+)/$', views.refresh_token, name = 'refresh_404_token'),
	url(r'^$', views.send_data, name='LnF_API'),
	url(r'^(?P<site_id>[0-9]+)/(?P<token>[a-zA-Z0-9]+)/$', views.send_data,),
)