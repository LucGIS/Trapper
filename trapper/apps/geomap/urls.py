from django.conf.urls import patterns, url
from django.views.generic import DetailView, UpdateView, ListView, CreateView, TemplateView, DeleteView

from trapper.apps.geomap import views


urlpatterns = patterns('',
	# Index view:
	url(r'^$', TemplateView.as_view(template_name='geomap/index.html'), name='index'),
	url(r'location/detail/(?P<pk>\d+)/$', views.LocationDetailView.as_view(), name='location_detail'),
	url(r'location/list/$', views.LocationListView.as_view(), name='location_list'),
	url(r'location/upload/$', views.LocationUploadView.as_view(), name='location_upload'),
)
