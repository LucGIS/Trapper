from django.conf.urls import patterns, url

from trapper.apps.storage import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'resource/view/(?P<pk>\d+)/$', views.ResourceView.as_view(), name='resource_view'),
	url(r'resource/update/(?P<pk>\d+)/$', views.ResourceUpdate.as_view(), name='resource_update'),
)
