from django.conf.urls import patterns, url

from trapper.apps.accounts import views

urlpatterns = patterns('',
	url(r'profile/$', views.profile_details , name='profile_details' ),
	url(r'login/$', 'django.contrib.auth.views.login', name='login' ),
	url(r'logout/$', views.logout_action, name='logout' ),
)
