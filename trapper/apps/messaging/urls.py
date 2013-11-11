from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView

from trapper.apps.messaging import views
from trapper.apps.messaging.models import Message

urlpatterns = patterns('',
	url(r'message/detail/(?P<pk>\d+)/$', views.MessageDetailView.as_view(), name='message_detail'),
	url(r'message/inbox/$', views.MessageInboxView.as_view(), name='message_inbox'),
	url(r'message/outbox/$', views.MessageOutboxView.as_view(), name='message_outbox'),
	url(r'message/create/$', views.MessageCreateView.as_view(), name='message_create'),
)
