from django.conf.urls import patterns, url
from django.views.generic import DetailView, UpdateView, ListView, CreateView, TemplateView, DeleteView

from trapper.apps.storage import views
from trapper.apps.storage.forms import ResourceForm, CollectionForm
from trapper.apps.storage.models import Resource, Collection


urlpatterns = patterns('',

	# Index view:
	url(r'^$', TemplateView.as_view(template_name='storage/index.html'), name='index'),

	# Resource views:
	url(r'resource/list/$', views.ResourceListView.as_view(), name='resource_list'),
	url(r'resource/list/(?P<user_pk>\d+)/$', views.UserResourceListView.as_view(), name='user_resource_list'),
	url(r'resource/detail/(?P<pk>\d+)/$', DetailView.as_view(model=Resource), name='resource_detail'),
	url(r'resource/update/(?P<pk>\d+)/$', views.ResourceUpdateView.as_view(), name='resource_update'),
	url(r'resource/create/$', views.ResourceCreateView.as_view(), name='resource_create'),
	url(r'resource/delete/(?P<pk>\d+)/$', views.ResourceDeleteView.as_view(), name='resource_delete'),

	# Collection views:
	url(r'collection/list/$', ListView.as_view(model=Collection, context_object_name='collections'), name='collection_list'),
	url(r'collection/list/(?P<user_pk>\d+)/$', views.UserCollectionListView.as_view(), name='user_collection_list'),
	url(r'collection/detail/(?P<pk>\d+)/$', DetailView.as_view(model=Collection), name='collection_detail'),
	url(r'collection/update/(?P<pk>\d+)/$', views.CollectionUpdateView.as_view(), name='collection_update'),
	url(r'collection/create/$', views.CollectionCreateView.as_view(), name='collection_create'),
	url(r'collection/delete/(?P<pk>\d+)$', views.CollectionDeleteView.as_view(), name='collection_delete'),
	url(r'collection/request/(?P<pk>\d+)/$', views.CollectionRequestView.as_view(), name='collection_request'),
)
