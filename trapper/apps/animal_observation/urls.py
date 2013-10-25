from django.conf.urls import patterns, url

from trapper.apps.animal_observation import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'project/view/(?P<project_id>\d+)/$', views.project_home, name='project_view'),
	url(r'classification/view/(?P<pk>\d+)/$', views.classification_view, name='classification_view'),
	url(r'classify/(?P<project_id>\d+)/(?P<resource_id>\d+)/$', views.classify_resource, name='classify_resource'),
	url(r'process_classify/$', views.process_classify, name='process_classify'),
)
