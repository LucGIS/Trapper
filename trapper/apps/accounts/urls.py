from django.conf.urls import patterns, url

from trapper.apps.accounts import views

urlpatterns = patterns('',
	url(r'profile/$', views.SessionUserProfileDetailView.as_view() , name='userprofile_detail' ),
	url(r'profile/detail/(?P<pk>\d+)/$', views.UserProfileDetailView.as_view() , name='userprofile_detail' ),
	url(r'profile/update/(?P<pk>\d+)/$', views.UserProfileUpdateView.as_view() , name='userprofile_update' ),
	url(r'login/$', 'django.contrib.auth.views.login', name='login' ),
	url(r'logout/$', views.logout_action, name='logout' ),
)
