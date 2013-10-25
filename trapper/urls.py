from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trapper.views.home', name='home'),
    url(r'^animal_observation/', include('trapper.apps.animal_observation.urls')),
    url(r'^storage/', include('trapper.apps.storage.urls')),
    #url(r'^accounts/', include('trapper.apps.accounts.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
