from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from trapper import views

admin.autodiscover()

urlpatterns = patterns('',
	# Trapper homepage
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),

	# Animal Observation urls
    url(r'^animal_observation/', include('trapper.apps.animal_observation.urls', namespace='animal_observation')),

	# Storage urls
    url(r'^storage/', include('trapper.apps.storage.urls', namespace='storage')),

	# Messaging urls
    url(r'^messaging/', include('trapper.apps.messaging.urls', namespace='messaging')),

	# Accounts urls
	url('', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('trapper.apps.accounts.urls', namespace='accounts')),

    url(r'^admin/', include(admin.site.urls)),
)
