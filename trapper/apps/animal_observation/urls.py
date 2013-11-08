from django.conf.urls import patterns, url

from trapper.apps.animal_observation import views

urlpatterns = patterns('',

	# Home page of animal observation app
	url(r'^$', views.index, name='trapper.apps.animal_observation.index'),

	# Display project list and the details about given project
	url(r'project/list/$', views.project_list, name='trapper.apps.animal_observation.project_list'),
	url(r'project/details/(?P<project_id>\d+)/$', views.project_details, name='trapper.apps.animal_observation.project_details'),
	url(r'project/update/(?P<project_id>\d+)/$', views.project_update, name='trapper.apps.animal_observation.project_update'),

	# Display the classification form and process (action) it
	url(r'classify/(?P<project_id>\d+)/(?P<resource_id>\d+)/$', views.classify_resource, name='trapper.apps.animal_observation.classify'),
	url(r'classify/action/$', views.process_classify, name='trapper.apps.animal_observation.classify_action'),

	# Displays the details about given classification
	url(r'classification/details/(?P<pk>\d+)/$', views.classification_details, name='trapper.apps.animal_observation.classification_details'),

	url(r'crowd/list/$', views.cs_resource_list, name='trapper.apps.animal_observation.cs_resource_list'),
)
