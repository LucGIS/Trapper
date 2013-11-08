from django.conf.urls import patterns, url

from trapper.apps.animal_observation import views

urlpatterns = patterns('',

	# Home page of animal observation app
	url(r'^$', views.index, name='index'),

	# Display project list and the details about given project
	url(r'project/list/$', views.project_list, name='project_list'),
	url(r'project/details/(?P<project_id>\d+)/$', views.project_details, name='project_details'),
	url(r'project/update/(?P<project_id>\d+)/$', views.project_update, name='project_update'),

	# Display the classification form and process (action) it
	url(r'classify/(?P<project_id>\d+)/(?P<resource_id>\d+)/$', views.classify_resource, name='classify'),
	url(r'classify/action/$', views.process_classify, name='classify_action'),

	# Displays the details about given classification
	url(r'classification/details/(?P<pk>\d+)/$', views.classification_details, name='classification_details'),

	url(r'crowd/list/$', views.cs_resource_list, name='cs_resource_list'),
)
