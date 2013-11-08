from django.conf.urls import patterns, url

from trapper.apps.storage import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'resource/list/$', views.resource_list, name='resource_list'),
	url(r'resource/details/(?P<pk>\d+)/$', views.ResourceDetails.as_view(), name='resource_details'),
	url(r'resource/update/(?P<pk>\d+)/$', views.ResourceUpdate.as_view(), name='resource_update'),
)
