from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView

from trapper.apps.messaging import views
from trapper.apps.messaging.models import Message, ResourceCollectionRequest, SystemNotification

urlpatterns = patterns('',
	url(r'message/detail/(?P<pk>\d+)/$', views.MessageDetailView.as_view(), name='message_detail'),
	url(r'message/inbox/$', views.MessageInboxView.as_view(), name='message_inbox'),
	url(r'message/outbox/$', views.MessageOutboxView.as_view(), name='message_outbox'),
	url(r'message/create/$', views.MessageCreateView.as_view(), name='message_create'),
	url(r'notification/list/$', views.SystemNotificationListView.as_view(), name='notification_list'),
	url(r'notification/resolve/(?P<pk>\d+)/$', views.ResolveClassificaionResourceRequestView.as_view(), name='notification_resolve'),
)
