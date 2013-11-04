from django.conf.urls import patterns, url

from trapper.apps.accounts import views

urlpatterns = patterns('',
	url(r'profile/$', views.profile_details , name='trapper.apps.accounts.profile_details' ),
	url(r'login/$', 'django.contrib.auth.views.login', name='trapper.apps.accounts.login' ),
	url(r'logout/$', views.logout_action, name='trapper.apps.accounts.logout' ),
)
