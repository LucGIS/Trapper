from ajax_select import urls as ajax_select_urls

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.gis import admin as admin_gis
from django.views.generic import TemplateView

from django.conf import settings


admin.autodiscover()

urlpatterns = patterns('',
	# Trapper homepage
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),

	# Media classification urls
    url(r'^media_classification/', include('trapper.apps.media_classification.urls', namespace='media_classification')),

	# Storage urls
    url(r'^storage/', include('trapper.apps.storage.urls', namespace='storage')),

	# Messaging urls
    url(r'^messaging/', include('trapper.apps.messaging.urls', namespace='messaging')),

	# Accounts urls
	url('', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('trapper.apps.accounts.urls', namespace='accounts')),

	# GeoMap urls
    url(r'^geomap/', include('trapper.apps.geomap.urls', namespace='geomap')),

    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_gis/', include(admin_gis.site.urls)),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT,}),
	)
