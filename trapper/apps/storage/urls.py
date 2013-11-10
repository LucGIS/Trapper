from django.conf.urls import patterns, url

from trapper.apps.storage import views

urlpatterns = patterns('',
	
	# Index page
	url(r'^$', views.IndexView.as_view(), name='index'),

	# Resource urls
	url(r'resource/list/$', views.ResourceListView.as_view(), name='resource_list'),
	url(r'resource/list/(?P<user_pk>\d+)/$', views.UserResourceListView.as_view(), name='user_resource_list'),
	url(r'resource/detail/(?P<pk>\d+)/$', views.ResourceDetailView.as_view(), name='resource_detail'),
	url(r'resource/update/(?P<pk>\d+)/$', views.ResourceUpdateView.as_view(), name='resource_update'),
	url(r'resource/create/$', views.ResourceCreateView.as_view(), name='resource_create'),

	# ResourceCollection urls
	url(r'resourcecollection/list/$', views.ResourceCollectionListView.as_view(), name='collection_list'),
	url(r'resourcecollection/list/(?P<user_pk>\d+)/$', views.UserResourceCollectionListView.as_view(), name='user_collection_list'),
	url(r'resourcecollection/detail/(?P<pk>\d+)/$', views.ResourceCollectionDetailView.as_view(), name='collection_detail'),
	url(r'resourcecollection/update/(?P<pk>\d+)/$', views.ResourceCollectionUpdateView.as_view(), name='collection_update'),
	url(r'resourcecollection/create/$', views.ResourceCollectionCreateView.as_view(), name='collection_create'),
)
