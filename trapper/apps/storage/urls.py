from django.conf.urls import patterns, url
from django.views.generic import DetailView, UpdateView, ListView, CreateView, TemplateView, DeleteView

from trapper.apps.storage import views
from trapper.apps.storage.models import Resource, ResourceCollection


urlpatterns = patterns('',
	# Index view:
	url(r'^$', TemplateView.as_view(template_name='storage/index.html'), name='index'),

	# Resource views:
	url(r'resource/list/$', ListView.as_view(model=Resource, context_object_name='resources'), name='resource_list'),
	url(r'resource/list/(?P<user_pk>\d+)/$', views.UserResourceListView.as_view(), name='user_resource_list'),
	url(r'resource/detail/(?P<pk>\d+)/$', DetailView.as_view(model=Resource), name='resource_detail'),
	url(r'resource/update/(?P<pk>\d+)/$', UpdateView.as_view(model=Resource, template_name='storage/resource_update.html'), name='resource_update'),
	url(r'resource/create/$', views.ResourceCreateView.as_view(), name='resource_create'),
	url(r'resource/delete/(?P<pk>\d+)$', DeleteView.as_view(model=Resource, success_url='resource/list/', context_object_name='object', template_name='storage/object_confirm_delete.html'), name='resource_delete'),

	# ResourceCollection views:
	url(r'resourcecollection/list/$', ListView.as_view(model=ResourceCollection, context_object_name='collections'), name='collection_list'),
	url(r'resourcecollection/list/(?P<user_pk>\d+)/$', views.UserResourceCollectionListView.as_view(), name='user_collection_list'),
	url(r'resourcecollection/detail/(?P<pk>\d+)/$', DetailView.as_view(model=ResourceCollection), name='collection_detail'),
	url(r'resourcecollection/update/(?P<pk>\d+)/$', UpdateView.as_view(model=ResourceCollection, template_name='storage/resourcecollection_update.html'), name='collection_update'),
	url(r'resourcecollection/create/$', CreateView.as_view(model=ResourceCollection, template_name='storage/resourcecollection_create.html'), name='collection_create'),
	url(r'resourcecollection/delete/(?P<pk>\d+)$', DeleteView.as_view(model=ResourceCollection, success_url='collection/list/', context_object_name='object', template_name='storage/object_confirm_delete.html'), name='collection_delete'),
	url(r'resourcecollection/request/(?P<pk>\d+)/$', views.ResourceCollectionRequestView.as_view(), name='collection_request'),
)
